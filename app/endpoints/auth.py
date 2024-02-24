from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Path, Depends
from fastapi.responses import RedirectResponse, Response
from starlette import status
from fastapi_mail import FastMail, MessageSchema, MessageType
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
    # redis = get_redis_client()
    # ref_id = uuid4()
    # # TODO TTL, atomic
    # redis.hset(f'ref_ids_{ref_id}', 'username', user_data.username)
    # redis.hset(f'ref_ids_{ref_id}', 'password_hash', hash_password(user_data.password))
    # email_message = MessageSchema(
    #     subject=f"Registration {ref_id}",
    #     recipients=[user_data.email],
    #     body=f"Please follow {settings.HOST}/api/v1/confirmation/{ref_id}",
    #     subtype=MessageType.plain,
    # )
    # fm = FastMail(mail_config)
    # await fm.send_message(email_message)
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


@router.get(
    path='/password_change_confirm/{confirmation_id}',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
)
async def change_password_confirmation(confirmation_id: Annotated[UUID, Path()]):
    """
    Change password email link
    """
    pass


@router.post(
    path='/authentication',
    status_code=status.HTTP_200_OK,
    response_model=AuthenticationOut,
)
async def authenticate(credentials: Annotated[AuthenticationIn, Body()]) -> AuthenticationOut:
    """
    Authenticate by credentials
    """
    pass


@router.post(
    path='/refresh',
    status_code=status.HTTP_200_OK,
    response_model=AuthenticationOut,
)
async def refresh() -> AuthenticationOut:
    """
    Refresh token
    """
    pass


@router.post(
    path='/password',
    status_code=status.HTTP_200_OK,
)
async def change_password(
        password_data: Annotated[PasswordUpdate, Body()],
):
    """
    Change password, no response body
    """
    pass


@router.get(
    path='/registration_request',
    status_code=status.HTTP_200_OK,
    response_model=list[RegistrationRequest],
)
async def get_registration_requests(
        pagination: Annotated[Pagination, Depends(pagination_dependency)],
) -> list[RegistrationRequest]:
    """
    Get teacher's registrations requests (Only for admin)
    """
    pass


@router.patch(
    path='/registration_request/{reg_request_id}',
    status_code=status.HTTP_200_OK,
)
async def accept_or_decline_registration_request(
        reg_request_id: Annotated[UUID, Path()],
):
    """
    Accept or decline teacher registration request (Only for admin)
    """
    pass
