import asyncio
from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas import CallbackServerRequest
from app.db import get_session
from app.db.models import SubmissionStatus, Submission, Attempt

router = APIRouter(
    prefix=''
)


STATUS_ID_MAP = {
    1: SubmissionStatus.IN_QUEUE,
    2: SubmissionStatus.IN_QUEUE,
    3: SubmissionStatus.ACCEPTED,
    4: SubmissionStatus.WRONG_ANSWER,
    5: SubmissionStatus.TIME_LIMIT_EXCEED,
    6: SubmissionStatus.COMPILATION_ERROR,
    7: SubmissionStatus.RUNTIME_ERROR,  # Segfault
    8: SubmissionStatus.RUNTIME_ERROR,  # File size
    9: SubmissionStatus.RUNTIME_ERROR,  # Float error
    10: SubmissionStatus.RUNTIME_ERROR,  # Abort error
    11: SubmissionStatus.RUNTIME_ERROR,  # Non-zero exit code
    12: SubmissionStatus.RUNTIME_ERROR,  # Other error
} | {i: SubmissionStatus.SERVICE_ERROR for i in range(13, 20)}


@router.put(
    path='/',
    status_code=status.HTTP_200_OK,
)
async def callback(
        message: CallbackServerRequest,
        session: Annotated[AsyncSession, Depends(get_session)],
):
    # wait for database
    await asyncio.sleep(2)
    attempt_id = await session.scalar(
        select(Submission.attempt_id).where(Submission.token == message.token)
    )
    attempt: Attempt = await session.scalar(
        select(Attempt).
        where(Attempt.id == attempt_id).
        with_for_update()
    )
    attempt.tests_completed += 1
    await session.flush()
    submission_status = STATUS_ID_MAP[message.status.id]
    await session.execute(
        update(Submission).
        where(Submission.token == message.token).
        values(
            status=submission_status,
            time=int(message.time * 1000),
            memory=message.memory,
        )
    )
    await session.flush()
    # if all tests completed
    if attempt.tests_completed == attempt.tests_needed and attempt.status == SubmissionStatus.IN_QUEUE:
        sibling_submissions = list(await session.scalars(
            select(Submission).
            where(Submission.attempt_id == attempt.id)
        ))
        counter = Counter()
        for subm in sibling_submissions:
            counter[subm.status] += 1
        # If any service error
        if counter[SubmissionStatus.SERVICE_ERROR] > 0:
            attempt.status = SubmissionStatus.SERVICE_ERROR
        # If all accepted
        elif counter[SubmissionStatus.ACCEPTED] == len(sibling_submissions):
            attempt.status = SubmissionStatus.ACCEPTED
        # First appropriate status (most common, != Accepted)
        else:
            for status, _ in counter.most_common():
                if status != SubmissionStatus.ACCEPTED:
                    attempt.status = status
                    break
    await session.commit()
