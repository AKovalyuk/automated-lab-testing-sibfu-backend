from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Path, Depends
from fastapi.responses import RedirectResponse
from starlette import status

from app.schemas import UserIn, AuthenticationIn, AuthenticationOut, PasswordUpdate, RegistrationRequest
from app.dependencies import pagination_dependency, Pagination


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
async def confirm_registration(confirmation_id: Annotated[UUID, Path()]):
    """
    Confirm registration (by click on link in email)
    """
    pass


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
        reg_request_id: Annotated[UUID, Path()],):
    """
    Accept or decline teacher registration request (Only for admin)
    """
    pass
