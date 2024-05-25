from typing import Annotated

from fastapi import APIRouter, Depends, Response
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    attempt: Attempt = submission.attempt
    submission_status = STATUS_ID_MAP[message.status.id]
    print(submission_status, message.status.id)
    #if STATUS_PRIORITY_MAP[submission_status] > STATUS_PRIORITY_MAP[attempt.status]:
    #    attempt.status = submission_status
    submission.status = submission_status
    submission.time = int(message.time * 1000)
    submission.memory = message.memory
    await session.flush()
    sibling_submission = list(await session.scalars(
        select(Submission).
        where(Submission.attempt_id == attempt.id)
    ))
    acc_count = 0
    wa_count = 0
    tle_count = 0
    mle_count = 0
    se_count = 0
    total_count = len(sibling_submission)
    for subm in sibling_submission:
        match subm.status:
            case SubmissionStatus.ACCEPTED:
                acc_count += 1
            case SubmissionStatus.MEMORY_LIMIT_EXCEED:
                mle_count += 1
            case SubmissionStatus.WRONG_ANSWER:
                wa_count += 1
            case SubmissionStatus.TIME_LIMIT_EXCEED:
                tle_count += 1
            case SubmissionStatus.SERVICE_ERROR:
                se_count += 1
    if attempt.status == SubmissionStatus.IN_QUEUE:
        if se_count > 0:
            attempt.status = SubmissionStatus.SERVICE_ERROR
        elif acc_count == total_count:
            attempt.status = SubmissionStatus.ACCEPTED
        elif acc_count + mle_count + wa_count + tle_count == total_count:
            attempt.status = max([
                (mle_count, SubmissionStatus.MEMORY_LIMIT_EXCEED),
                (wa_count, SubmissionStatus.WRONG_ANSWER),
                (tle_count, SubmissionStatus.TIME_LIMIT_EXCEED)
            ])[1]
    await session.commit()
