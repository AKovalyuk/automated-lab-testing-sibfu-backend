from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Path, Depends
from starlette import status

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
) -> UserOut:
    return UserOut(
        id=user_id,
        username=user.username,
        display_name=user.display_name,
        is_teacher=user.is_teacher,
        email=user.email,
    )


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
