from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Path, Depends
from fastapi.responses import RedirectResponse, Response
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import UserIn, AuthenticationIn, AuthenticationOut, PasswordUpdate, RegistrationRequest
from app.dependencies import pagination_dependency, Pagination
from app.config import mail_config, get_redis_client, settings
from app.utils.auth import hash_password, create_user, create_user_with_hashed_password
from app.db import get_session, User

router = APIRouter(prefix='', tags=['Authentication'])


@router.post(
    path='/registration',
)
async def register_user(user_data: Annotated[UserIn, Body()], session: Annotated[AsyncSession, Depends(get_session)]):
    # Check user exists
    if await session.scalar(select(User).filter_by(username=user_data.username)):
        return Response(
            status_code=status.HTTP_409_CONFLICT,
            content="Username is already taken.",
        )
    if await session.scalar(select(User).filter_by(email=user_data.email)):
        return Response(
            status_code=status.HTTP_409_CONFLICT,
            content="Email is already taken.",
        )
    await create_user(
        password=user_data.password,
        session=session,
        display_name=user_data.display_name,
        username=user_data.username,
        is_teacher=user_data.is_teacher,
        email=user_data.email,
    )
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    path='/confirmation/{confirmation_id}',
    status_code=status.HTTP_200_OK,
    response_class=RedirectResponse,
    deprecated=True,
)
async def confirm_registration(
        confirmation_id: Annotated[UUID, Path()],
        session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Confirm registration (by click on link in email)
    """
    redis = get_redis_client()
    data = redis.hgetall(f'ref_ids_{confirmation_id}')
    if 'password_hash' in data:
        await create_user_with_hashed_password(
            session=session,
            **data,
        )
        return Response('You\'re successfully confirmed your registration', status_code=status.HTTP_200_OK)
