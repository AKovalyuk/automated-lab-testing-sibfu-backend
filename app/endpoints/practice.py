from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import PracticeIn, PracticeOut
from app.dependencies.pagination import pagination_dependency, Pagination
from app.db import Practice, Course, User, get_session
from app.dependencies import auth_dependency
from app.utils import practice_has_write_permission, practice_has_read_permission, is_participant


router = APIRouter(
    prefix='',
    tags=['Practice'],
)


@router.get(
    path='/practice/{practice_id}',
    response_model=PracticeOut,
    status_code=status.HTTP_200_OK,
)
async def get_practice(
        practice_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> PracticeOut:
    practice = await session.scalar(
        select(Practice).
        where(Practice.id == practice_id)
    )
    if practice:
        if await practice_has_read_permission(user, practice, session):
            return PracticeOut.model_validate(practice)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get(
    path='/course/{course_id}/practice',
    response_model=list[PracticeOut],
    status_code=status.HTTP_200_OK,
)
async def get_practice_list(
        course_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        pagination: Annotated[Pagination, Depends(pagination_dependency)],
) -> list[PracticeOut]:
    """
    Get course practices in deadline order
    """
    course = await session.get(Course, ident=course_id)
    if course:
        if await is_participant(course, user, session):
            results = await session.execute(
                select(Practice.__table__.c).
                where(Practice.course_id == course_id).
                limit(pagination.size).
                offset(pagination.size * (pagination.page - 1)).
                order_by(Practice.deadline)
            )
            return [
                PracticeOut(**result) for result in results.mappings()
            ]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post(
    path='/course/{course_id}/practice',
    status_code=status.HTTP_201_CREATED,
    response_model=PracticeOut,
)
async def create_practice(
        course_id: Annotated[UUID, Path()],
        practice_data: Annotated[PracticeIn, Body()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> PracticeOut:
    course = await session.get(Course, ident=course_id)
    if course:
        if user.is_teacher and await is_participant(course, user, session):
            new_practice = Practice(**practice_data.model_dump())
            new_practice.course = course
            new_practice.author_id = user.id
            session.add(new_practice)
            await session.commit()
            return PracticeOut.model_validate(new_practice)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete(
    path='/practice/{practice_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_practice(
        practice_id: Annotated[UUID, Path()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
):
    practice = await session.scalar(
        select(Practice).
        where(Practice.id == practice_id)
    )
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    course = await session.get(Course, ident=practice.course_id)
    if course and practice and practice.course_id == course.id:
        if practice_has_write_permission(user, practice, session):
            await session.delete(practice)
            await session.commit()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put(
    path='/practice/{practice_id}',
    status_code=status.HTTP_200_OK,
    response_model=PracticeOut,
)
async def edit_practice(
        practice_id: Annotated[UUID, Path()],
        practice_data: Annotated[PracticeIn, Body()],
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> PracticeOut:
    """
    Edit practice data
    """
    practice = await session.get(Practice, ident=practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if await practice_has_write_permission(user, practice, session):
        for field_name, field_value in practice_data.model_dump().items():
            setattr(practice, field_name, field_value)
        await session.commit()
        return PracticeOut.model_validate(practice)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
