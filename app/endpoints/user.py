from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Path, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import UserIn, UserOut
from app.dependencies import auth_dependency
from app.db.models import User


router = APIRouter(prefix='/user', tags=['User'])


@router.get(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
async def get_user(
        user_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> UserOut:
    user_from_db = await session.get(User, ident=user_id)
    if user_from_db:
        return UserOut(
            id=user_from_db.id,
            username=user_from_db.username,
            display_name=user_from_db.display_name,
            is_teacher=user_from_db.is_teacher,
            email=user_from_db.email,
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
async def edit_user(
        user_id: Annotated[UUID, Path()],
        user_data: Annotated[UserIn, Body()]
) -> UserOut:
    """
    Edit user data
    """
    pass


@router.get(
    path='/me',
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
async def get_me(
        user: Annotated[User, Depends(auth_dependency)],
):
    return UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        is_teacher=user.is_teacher,
        email=user.email,
    )
