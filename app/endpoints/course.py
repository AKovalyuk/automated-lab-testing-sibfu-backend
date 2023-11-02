from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body
from starlette import status

from app.schemas.course import CourseOut, CourseIn


router = APIRouter(
    prefix='/course',
    tags=['Course'],
)


@router.get(
    path='/{course_id}',
    response_model=CourseOut,
    status_code=status.HTTP_200_OK,
)
async def get_course(course_id: Annotated[UUID, Path()]) -> CourseOut:
    """
    Get course by id
    """
    pass


@router.post(
    path='/',
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(course_data: Annotated[CourseIn, Body()]) -> CourseOut:
    """
    Endpoint for course creation
    """
    pass


@router.patch(
    path='/{course_id}',
    response_model=CourseOut,
    status_code=status.HTTP_200_OK,
)
async def edit_course(
        course_id: Annotated[UUID, Path()],
        course_data: Annotated[CourseIn, Body()]
) -> CourseOut:
    """
    Endpoint for course edit
    """
    pass


@router.delete(
    path='/{course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_course(course_id: Annotated[UUID, Path()]):
    """
    Delete course endpoint
    """
    pass
