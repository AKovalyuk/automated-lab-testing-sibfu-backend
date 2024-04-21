from uuid import UUID
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Path, Depends, Body, HTTPException, status, Response
from starlette import status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.db import get_session, User, Practice, Course, Participation, Submission, SubmissionStatus, Attempt
from app.dependencies import auth_dependency
from app.schemas import AttemptOut, AttemptIn
from app.config import settings

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
        where(Participation.user_id == user.id)
    )
    if not participation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if attempt_data.language_id not in practice.languages:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Language with id={attempt_data.language_id} not allowed for this practice",
        )
    # Create attempt object
    attempt = Attempt(
        language_id=attempt_data.language_id,
        meta={},
        sent_time=datetime.now(),
        author_id=user.id,
        practice_id=practice_id,
        status=SubmissionStatus.IN_QUEUE
    )
    session.add(attempt)
    await session.commit()
    submissions = []
    # Preparing data for multiple submission
    for testcase in practice.testcases:
        submissions.append(
            {
                "source_code": attempt_data.source_code,
                "language_id": attempt_data.language_id,
                "memory_limit": practice.memory_limit,
                "cpu_time_limit": practice.time_limit / 1000,
                "excepted_output": testcase.excepted,
                "stdin": testcase.input,
                "network": practice.network,
                "max_threads": practice.max_threads,
                "callback_url": f"{settings.CALLBACK_URL}:{settings.APP_PORT}",
            }
        )
    # Send multiple submissions in one request
    async with AsyncClient() as client:
        response = await client.post(
            url=f"{settings.JUDGE0_HOST}:{settings.JUDGE0_PORT}/submissions",
            params={
                "base64_encoded": "false",
                "wait": "false",
            },
            json={
                "submissions": submissions,
            }
        )
        if response.status_code in (200, 201):
            tokens = [submission_info["token"] for submission_info in response.json()]
            submissions = [
                Submission(
                    token=token,
                    status=SubmissionStatus.IN_QUEUE,
                    time=0,
                    memory=0,
                    attempt_id=attempt.id,
                )
                for token in tokens
            ]
            session.add_all(submissions)
            await session.commit()
            return Response(status_code=status.HTTP_201_CREATED)
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@router.get(
    path='/practice/{practice_id}/attempt',
    response_model=list[AttemptOut],
    status_code=status.HTTP_200_OK,
)
async def get_attempts(
        practice_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> list[AttemptOut]:
    practice = await session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    attempts = await session.scalars(
        select(Attempt).
        where(Attempt.author_id == user.id).
        where(Attempt.practice_id == practice.id).
        order_by(desc(Attempt.sent_time))
    )
    return [
        AttemptOut.model_validate(attempt)
        for attempt in attempts
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
    pass
