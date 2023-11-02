from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Path
from starlette import status

from app.schemas import UserIn, UserOut


router = APIRouter(prefix='/user', tags=['User'])


@router.get(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
async def get_user(user_id: Annotated[UUID, Path()]):
    """
    Get user info by id
    """
    pass


@router.patch(
    path='/{user_id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserOut,
)
async def edit_user(user_id: Annotated[UUID, Path()], user_data: Annotated[UserIn, Body()]):
    """
    Edit user data
    """
    pass
