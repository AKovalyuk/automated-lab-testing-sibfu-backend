from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends, Query, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from app.dependencies import auth_dependency
from app.schemas.course import (
    CourseOut,
    CourseIn,
    ParticipationOut,
    ParticipationIn,
    Summary,
    CourseSearchResult,
    ParticipationStatus,
)
from app.dependencies.pagination import pagination_dependency, Pagination
from app.db import get_session, Course, User, Participation
from app.utils import get_course_permission, CoursePermission, is_participant


router = APIRouter(
    prefix='/course',
    tags=['Course'],
)


@router.get(
    path='/search',
    status_code=status.HTTP_200_OK,
    response_model=list[CourseSearchResult],
)
async def search_course(
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        search: Annotated[str, Query()] = None,
):
    query = select(Course)
    if search:
        query = query.where(func.lower(Course.name).startswith(search.lower()))
    results = await session.scalars(query)
    return [
        CourseSearchResult(
            id=result.id,
            name=result.name,
            description=result.description,
            image_id=result.image_id,
            participation_status=ParticipationStatus.NONE,
        ) for result in results
    ]


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
    if course_in_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # Check permission
    if (await get_course_permission(course_in_db, user, session) in
            (CoursePermission.WRITE, CoursePermission.READ)):
        return CourseOut(
            id=course_in_db.id,
            name=course_in_db.name,
            description=course_in_db.description,
            image_id=course_in_db.image_id,
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


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
    results = await session.scalars(
        select(Course).
        join(Participation).
        where(Participation.user_id == user.id).
        where(Participation.is_request == False)
    )
    return [
        CourseOut(
            id=course.id,
            name=course.name,
            description=course.description,
            image_id=course.image_id,
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
        new_course = Course(
            name=course_data.name,
            description=course_data.description,
            image_id=course_data.image_id,
        )
        session.add(new_course)
        await session.flush()
        session.add(Participation(user_id=user.id, course_id=new_course.id))
        await session.commit()
        return CourseOut(
            id=new_course.id,
            name=new_course.name,
            description=new_course.description,
            image_id=new_course.image_id,
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.put(
    path='/{course_id}',
    response_model=CourseOut,
    status_code=status.HTTP_200_OK,
)
async def edit_course(
    user: Annotated[User, Depends(auth_dependency)],
    course_id: Annotated[UUID, Path()],
    course_data: Annotated[CourseIn, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CourseOut:
    course = await session.get(Course, ident=course_id)

    # Check course exists
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Check permission
    if await get_course_permission(course, user, session) == CoursePermission.WRITE:
        course.description = course_data.description
        course.name = course_data.name
        course.image_id = course_data.image_id
        await session.commit()
        return CourseOut(
            id=course.id,
            name=course.name,
            description=course.description,
            image_id=course.image_id,
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


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
        if user.is_teacher and await is_participant(course, user, session):
            await session.delete(course)
            await session.commit()
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch(
    path='/{course_id}/participation',
    status_code=status.HTTP_200_OK,
)
async def course_participation_request(
    course_id: Annotated[UUID, Path()],
    user: Annotated[User, Depends(auth_dependency)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Participation in course
    (PATCH method used for idempotency)
    """
    course = await session.get(Course, ident=course_id)
    # Check exists
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    participation = await session.scalar(
        select(Participation).
        where(Participation.course_id == course_id).
        where(Participation.user_id == user.id)
    )
    if not participation:
        session.add(Participation(user_id=user.id, course_id=course_id, is_request=True))
        await session.commit()


@router.get(
    path='/{course_id}/participation',
    status_code=status.HTTP_200_OK,
    response_model=list[ParticipationOut],
)
async def get_participation(
        course_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        pagination: Annotated[Pagination, Depends(pagination_dependency)],
) -> list[ParticipationOut]:
    course = await session.get(Course, ident=course_id)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if course:
        results = await session.execute(
            select(User.__table__.c, Participation.is_request.label('is_request'), Participation.user_id).
            join(Participation).
            where(Participation.course_id == course_id).
            limit(pagination.size).
            offset(pagination.size * (pagination.page - 1))
        )
        return [
            ParticipationOut(**result) for result in results.mappings()
        ]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch(
    path='/{course_id}/participation_update',
    status_code=status.HTTP_200_OK,
)
async def update_participation(
        course_id: Annotated[UUID, Path()],
        participation_data: list[ParticipationIn],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
):
    course = await session.get(Course, ident=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if user.is_teacher and await is_participant(course, user, session):
        approve_ids = [
            command.user_id for command in participation_data if command.status == "approve"
        ]
        remove_ids = [
            command.user_id for command in participation_data if command.status == "remove"
        ]
        await session.execute(
            update(Participation).
            where(Participation.course_id == course_id).
            where(Participation.user_id.in_(approve_ids)).
            values(is_request=False)
        )
        await session.execute(
            delete(Participation).
            where(Participation.course_id == course_id).
            where(Participation.user_id.in_(remove_ids))
        )
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


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
