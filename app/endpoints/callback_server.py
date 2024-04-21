from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CallbackServerRequest
from app.db import get_session
from app.db.models import SubmissionStatus, Submission, Attempt

router = APIRouter(
    prefix=''
)


# TODO MEMORY_LIMIT
# TODO FIX TO DEFAULTDICT
STATUS_ID_MAP = {
    1: SubmissionStatus.IN_QUEUE,
    2: SubmissionStatus.IN_QUEUE,
    3: SubmissionStatus.ACCEPTED,
    4: SubmissionStatus.WRONG_ANSWER,
    5: SubmissionStatus.TIME_LIMIT_EXCEED,
    6: SubmissionStatus.COMPILATION_ERROR,
} | {i: SubmissionStatus.SERVICE_ERROR for i in range(7, 20)}
STATUS_PRIORITY_MAP = {
    SubmissionStatus.ACCEPTED: 0,
    SubmissionStatus.IN_QUEUE: 1,
    SubmissionStatus.TIME_LIMIT_EXCEED: 2,
    SubmissionStatus.MEMORY_LIMIT_EXCEED: 2,
    SubmissionStatus.WRONG_ANSWER: 3,
    SubmissionStatus.COMPILATION_ERROR: 4,
    SubmissionStatus.SERVICE_ERROR: 5,
}


@router.put(
    path='/',
    status_code=status.HTTP_200_OK,
)
async def callback(
        message: CallbackServerRequest,
        session: Annotated[AsyncSession, Depends(get_session)],
):
    submission = await session.get(Submission, message.token)
    async with session.begin():
        attempt: Attempt = submission.attempt
        submission_status = STATUS_ID_MAP[message.status.id]
        if STATUS_PRIORITY_MAP[submission_status] > STATUS_PRIORITY_MAP[attempt.status]:
            attempt.status = submission_status
        submission.status = submission_status
        submission.time = int(message.time * 1000)
        submission.memory = message.memory
    if all(subm.status == SubmissionStatus.ACCEPTED for subm in attempt.submissions):
        attempt.status = SubmissionStatus.ACCEPTED
        await session.commit()
