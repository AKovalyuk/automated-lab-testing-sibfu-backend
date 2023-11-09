from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends, Query
from starlette import status

from app.schemas.course import CourseOut, CourseIn, ParticipationOut, ParticipationIn, Summary
from app.dependencies.pagination import pagination_dependency, Pagination


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


@router.get(
    path='/',
    response_model=list[CourseOut],
    status_code=status.HTTP_200_OK,
)
async def get_courses(
        pagination: Annotated[Pagination, Depends(pagination_dependency)],
) -> list[CourseOut]:
    """
    List courses with pagination
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


@router.put(
    path='/{course_id}/participation',
    status_code=status.HTTP_200_OK,
)
async def course_participation_request(
        course_id: Annotated[UUID, Path()],
):
    """
    Participation in course
    (PATCH method used for idempotency)
    """
    pass


@router.get(
    path='/{course_id}/participation',
    status_code=status.HTTP_200_OK,
    response_model=list[ParticipationOut],
)
async def get_participation(
        course_id: Annotated[UUID, Path()],
) -> list[ParticipationOut]:
    """
    Get participants (students) for this course
    """
    pass


@router.patch(
    path='/{course_id}/participation',
    status_code=status.HTTP_200_OK,
)
async def update_participation(
        course_id: Annotated[UUID, Path()],
        participation_data: list[ParticipationIn],
) -> list[ParticipationOut]:
    """
    Change list of course participants
    """
    pass


@router.delete(
    path='/{course_id}/participation',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_participation(
        course_id: Annotated[UUID, Path()],
        remove_progress: Annotated[bool, Query(
            description="Delete participation with student's progress?"
        )],
        delete_ids: Annotated[list[UUID], Body()],
):
    """
    Remove student's participation from course
    """
    pass


@router.get(
    path='/{course_id}/summary',
    status_code=status.HTTP_200_OK,
    response_model=list[Summary],
)
async def summary(
        course_id: Annotated[UUID, Path()],
) -> list[Summary]:
    """
    Get summary about students
    """
    pass
