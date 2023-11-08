from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends
from starlette import status

from app.schemas import PracticeIn, PracticeOut
from app.dependencies.pagination import pagination_dependency, Pagination


router = APIRouter(
    prefix='',
    tags=['Practice'],
)


@router.get(
    path='/course/{course_id}/practice/{practice_id}',
    response_model=PracticeOut,
    status_code=status.HTTP_200_OK,
)
async def get_practice(
        course_id: Annotated[UUID, Path()],
        practice_id: Annotated[UUID, Path()]
) -> PracticeOut:
    """
    Get practice by id
    """
    pass


@router.get(
    path='/course/{course_id}/practice',
    response_model=list[PracticeOut],
    status_code=status.HTTP_200_OK,
)
async def get_practice_list(
        course_id: UUID,
        pagination: Annotated[Pagination, Depends(pagination_dependency)],
) -> list[PracticeOut]:
    """
    Get course practices in deadline order
    """
    pass


@router.post(
    path='/course/{course_id}/practice',
    status_code=status.HTTP_201_CREATED,
    response_model=PracticeOut,
)
async def create_practice(
        course_id: Annotated[UUID, Path()],
        practice_data: Annotated[PracticeIn, Body()],
) -> PracticeOut:
    """
    Create practice
    """


@router.delete(
    path='/course/{course_id}/practice/{practice_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_practice(
        course_id: Annotated[UUID, Path()],
        practice_id: Annotated[UUID, Path()],
):
    """
    Delete practice by id
    """
    pass


@router.patch(
    path='/course/{course_id}/practice/{practice_id}',
    status_code=status.HTTP_200_OK,
    response_model=PracticeOut,
)
async def edit_practice(
        course_id: Annotated[UUID, Path()],
        practice_id: Annotated[UUID, Path()],
        practice_data: Annotated[PracticeIn, Body()],
) -> PracticeOut:
    """
    Edit practice data
    """
    pass
