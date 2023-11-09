from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Query
from starlette import status

from app.schemas import AttemptOut, AttemptIn


router = APIRouter(
    prefix='',
    tags=['Attempt'],
)


@router.post(
    path='/practice/{practice_id}/attempt',
    status_code=status.HTTP_201_CREATED,
)
async def send_attempt(
        practice_id: Annotated[UUID, Path()],
        compressed: Annotated[bool, Query(
            title="Flag = is archive sent?"
        )],
        language_id: Annotated[UUID, Query()],
) -> AttemptOut:
    """
    Send code for testing
    """
    pass


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
