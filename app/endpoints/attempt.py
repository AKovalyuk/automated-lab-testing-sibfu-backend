from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Depends, Body, HTTPException, status, Response
from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.db import get_session, User, Practice, Course, Participation
from app.dependencies import auth_dependency
from app.schemas import AttemptOut, AttemptIn
from app.config import settings


router = APIRouter(
    prefix='',
    tags=['Attempt'],
)


@router.post(
    path='/practice/attempt',
    status_code=status.HTTP_201_CREATED,
)
async def send_attempt(
        # practice_id: Annotated[UUID, Path()],
        # user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
): #-> AttemptOut:
    """
    Send code for testing
    """
    # practice = await session.get(Practice, ident=practice_id)
    # if not practice:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # participation = await session.scalar(
    #     select(Participation).
    #     where(Participation.course_id == practice.course_id).
    #     where(Participation.user_id == user.id)
    # )
    # if not participation:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    async with AsyncClient() as client:
        response = await client.post(
            url=f"{settings.JUDGE0_HOST}:{settings.JUDGE0_PORT}/submissions",
            params={
                "base64_encoded": "false",
                "wait": "false",
            },
            json={
                "source_code": "print('hello world')",
                "language_id": 71,
                "memory_limit": 128000,
                "cpu_time_limit": 1,
                "excepted_output": "hello world",
                "callback_url": f"{settings.CALLBACK_URL}:{settings.APP_PORT}",
            }
        )
    return Response(status_code=status.HTTP_200_OK)



@router.get(
    path='/practice/{practice_id}/attempt',
    response_model=list[AttemptOut],
    status_code=status.HTTP_200_OK,
)
async def get_attempts(
        practice_id: Annotated[UUID, Path()],
) -> list[AttemptOut]:
    """
    Get results of all attempts
    """
    pass


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
