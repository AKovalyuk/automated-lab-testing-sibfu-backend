from uuid import UUID
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Path, Depends, Body, HTTPException, status, Response
from starlette import status
from sqlalchemy import select, desc, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.config.languages import LANGUAGES
from app.db import get_session, User, Practice, Course, Participation, Submission, SubmissionStatus, Attempt
from app.dependencies import auth_dependency, Pagination, pagination_dependency
from app.schemas import AttemptOut, AttemptIn, PaginationResult, AttemptSummary
from app.config import settings
from app.utils import send_parallel_post

router = APIRouter(
    prefix='',
    tags=['Attempt'],
)


@router.post(
    path='/practice/{practice_id}/attempt',
    status_code=status.HTTP_201_CREATED,
)
async def send_attempt(
        practice_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        attempt_data: Annotated[AttemptIn, Body()],
):
    """
    Send code for testing
    """
    practice = await session.get(Practice, ident=practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    participation = await session.scalar(
        select(Participation).
        where(Participation.course_id == practice.course_id).
        where(Participation.user_id == user.id).
        where(Participation.is_request == False)
    )
    if not participation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if attempt_data.language_id not in practice.languages:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Language with id={attempt_data.language_id} not allowed for this practice",
        )
    # Get testcases
    testcases = list(practice.testcases)
    # Create attempt object
    attempt = Attempt(
        language_id=attempt_data.language_id,
        meta={},
        sent_time=datetime.now(),
        author_id=user.id,
        practice_id=practice_id,
        status=SubmissionStatus.IN_QUEUE,
        tests_needed=len(testcases),
        tests_completed=0,
    )
    session.add(attempt)
    await session.commit()
    submissions = []
    # Preparing data for multiple submission
    for testcase in testcases:
        submissions.append(
            {
                "source_code": attempt_data.source_code,
                "language_id": LANGUAGES[attempt_data.language_id].judge0id,
                "memory_limit": practice.memory_limit,
                "cpu_time_limit": practice.time_limit / 1000,
                "expected_output": testcase.excepted,
                "stdin": testcase.input,
                "network": practice.network,
                "max_threads": practice.max_threads,
                "callback_url": f"{settings.CALLBACK_URL}:{settings.APP_PORT}",
            }
        )
    # Lock row to create queue
    await session.execute(
        select(Attempt).
        where(Attempt.id == attempt.id).
        with_for_update()
    )
    # Send multiple submissions in one request
    async with AsyncClient() as client:
        responses = await send_parallel_post(
            client=client,
            url=f"{settings.JUDGE0_HOST}:{settings.JUDGE0_PORT}/submissions",
            jsons=submissions,
        )
    # Check service availability
    for response in responses:
        if response.status_code not in (200, 201):
            print(response)
            # if service not available: mark attempt as service error
            attempt.status = SubmissionStatus.SERVICE_ERROR
            await session.commit()
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    submission_instances = []
    for response in responses:
        token = response.json()["token"]
        submission_instances.append(
            Submission(
                token=token,
                status=SubmissionStatus.IN_QUEUE,
                time=0,
                memory=0,
                attempt_id=attempt.id,
            )
        )
    session.add_all(submission_instances)
    await session.commit()


@router.get(
    path='/practice/{practice_id}/attempt',
    response_model=PaginationResult[AttemptOut],
    status_code=status.HTTP_200_OK,
)
async def get_attempts(
        practice_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        pagination: Annotated[Pagination, Depends(pagination_dependency)],
) -> PaginationResult[AttemptOut]:
    practice = await session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    attempts = await session.scalars(
        select(Attempt).
        where(Attempt.author_id == user.id).
        where(Attempt.practice_id == practice.id).
        order_by(desc(Attempt.sent_time)).
        limit(pagination.size).
        offset(pagination.size * (pagination.page - 1))
    )
    count = await session.scalar(
        select(func.count()).
        select_from(Attempt).
        where(Attempt.author_id == user.id).
        where(Attempt.practice_id == practice.id)
    )
    return PaginationResult[AttemptOut](
        count=count,
        results=[
            AttemptOut.model_validate(attempt)
            for attempt in attempts
        ]
    )


@router.get(
    path='/practice/{practice_id}/summary',
    status_code=status.HTTP_200_OK,
)
async def get_practice_summary(
        practice_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> list[AttemptSummary]:
    practice = await session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    query = text("""
        SELECT "user".id AS user_id, "user".display_name, 
        (SELECT COUNT(*) FROM attempt WHERE attempt.status = :accept_status) AS accept_count 
        FROM "user" WHERE "user".id IN (
            SELECT participation.user_id FROM participation JOIN "user" ON participation.user_id = "user".id
            WHERE participation.course_id = :course_id AND NOT participation.is_request AND NOT "user".is_teacher
        );
    """)
    results = await session.execute(
        statement=query,
        params={
            "course_id": practice.course_id,
            "accept_status": SubmissionStatus.ACCEPTED,
        }
    )
    return [
        AttemptSummary(
            user_id=result["user_id"],
            display_name=result["display_name"],
            accepted=result["accept_count"] > 0,
        )
        for result in results.mappings()
    ]


@router.get(
    path='/practice/{practice_id}/attempt/{attempt_id}',
    response_model=AttemptOut,
    status_code=status.HTTP_200_OK,
)
async def get_attempt_detailed(
        practice_id: Annotated[UUID, Path()],
        attempt_id: Annotated[UUID, Path()],
) -> AttemptOut:
    """
    Get detailed information about attempt
    """
