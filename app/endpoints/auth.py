from typing import Annotated

from fastapi import APIRouter, Body, Path
from fastapi.responses import RedirectResponse
from starlette import status

from app.schemas import UserIn, AuthenticationIn, AuthenticationOut


router = APIRouter(prefix='', tags=['Authentication'])


@router.post(
    path='/registration',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def register_user(user_data: Annotated[UserIn, Body()]):
    """
    Register user in service (send email)
    """
    pass


@router.get(
    path='/confirmation/{confirmation_id}',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse
)
async def confirm_registration(confirmation_id: Annotated[int, Path()]):
    """
    Confirm registration (by click on link in email)
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
