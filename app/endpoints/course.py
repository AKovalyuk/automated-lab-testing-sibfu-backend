from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends, Query, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import auth_dependency
from app.schemas.course import CourseOut, CourseIn, ParticipationOut, ParticipationIn, Summary
from app.dependencies.pagination import pagination_dependency, Pagination
from app.db import get_session, Course, User, Participation

router = APIRouter(
    prefix='/course',
    tags=['Course'],
)


@router.get(
    path='/{course_id}',
    response_model=CourseOut,
    status_code=status.HTTP_200_OK,
)
async def get_course(
    user: Annotated[User, Depends(auth_dependency)],
    course_id: Annotated[UUID, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CourseOut:
    """
    Get course by id
    """
    course_in_db = await session.get(Course, ident=course_id)
    # Check course exists
    if course_in_db:
        # Check
        if user.is_teacher or user in course_in_db.participants:
            return CourseOut(
                id=course_in_db.id,
                name=course_in_db.name,
                description=course_in_db.description,
            )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get(
    path='/',
    response_model=list[CourseOut],
    status_code=status.HTTP_200_OK,
)
async def get_courses(
    user: Annotated[User, Depends(auth_dependency)],
    pagination: Annotated[Pagination, Depends(pagination_dependency)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[CourseOut]:
    # TODO pagination
    """
    Get user's courses
    """
    if user.is_teacher:
        results = await session.scalars(
            select(Course)
        )
    else:
        results = await session.scalars(
            # TODO SELECT DISTINCT?
            select(Course).join(Participation).where(Participation.user_id == user.id)
        )
    return [
        CourseOut(
            id=course.id,
            name=course.name,
            description=course.description,
        ) for course in results
    ]


@router.post(
    path='/',
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
    user: Annotated[User, Depends(auth_dependency)],
    course_data: Annotated[CourseIn, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CourseOut:
    """
    Only teachers can create new courses
    """
    if user.is_teacher:
        new_course = Course(name=course_data.name, description=course_data.description)
        session.add(new_course)
        await session.flush()
        session.add(Participation(user_id=user.id, course_id=new_course.id))
        await session.commit()
        return CourseOut(
            id=new_course.id,
            name=new_course.name,
            description=new_course.description,
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.patch(
    path='/{course_id}',
    response_model=CourseOut,
    status_code=status.HTTP_200_OK,
)
async def edit_course(
    user: Annotated[User, Depends(auth_dependency)],
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
async def delete_course(
    course_id: Annotated[UUID, Path()],
    user: Annotated[User, Depends(auth_dependency)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Delete course endpoint (allowed only for teacher, participated in course)
    """
    course = await session.get(Course, ident=course_id)
    if course:
        if user.is_teacher and user in course.participants:
            await session.delete(course)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


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
