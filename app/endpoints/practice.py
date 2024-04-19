from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import PracticeIn, PracticeOut, Language
from app.dependencies.pagination import pagination_dependency, Pagination
from app.db import Practice, Course, User, get_session
from app.dependencies import auth_dependency
from app.utils import practice_has_write_permission, practice_has_read_permission, is_participant
from app.config.languages import ARCHIVED, LANGUAGES


router = APIRouter(
    prefix='',
    tags=['Practice'],
)


def get_practice_languages(practice: Practice) -> list[Language]:
    return [
        Language(id=lang_id, name=LANGUAGES[lang_id].name)
        for lang_id in practice.languages
        if lang_id not in ARCHIVED.keys()
    ]


def filter_languages(languages: list[int]) -> list[int]:
    return [
        lang_id for lang_id in languages
        if (lang_id in LANGUAGES) and (lang_id not in ARCHIVED.keys())
    ]


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
            result = PracticeOut.model_validate(practice)
            result.languages = get_practice_languages(practice)
            return result
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
            practice_data.languages = filter_languages(practice_data.languages)
            new_practice = Practice(**practice_data.model_dump())
            new_practice.course = course
            new_practice.author_id = user.id
            session.add(new_practice)
            await session.commit()
            return PracticeOut(
                id=new_practice.id,
                name=new_practice.name,
                description=new_practice.description,
                deadline=new_practice.deadline,
                soft_deadline=new_practice.soft_deadline,
                course_id=new_practice.course_id,
                author_id=new_practice.author_id,
                languages=get_practice_languages(new_practice),
                memory_limit=new_practice.memory_limit,
                time_limit=new_practice.time_limit,
                max_threads=new_practice.max_threads,
                command_line_args=new_practice.command_line_args,
                network=new_practice.network,
                allow_multi_file=new_practice.allow_multi_file,
            )
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
        practice_data.languages = filter_languages(practice_data.languages)
        for field_name, field_value in practice_data.model_dump().items():
            setattr(practice, field_name, field_value)
        await session.commit()
        return PracticeOut(
            id=practice.id,
            name=practice.name,
            description=practice.description,
            deadline=practice.deadline,
            soft_deadline=practice.soft_deadline,
            course_id=practice.course_id,
            author_id=practice.author_id,
            languages=get_practice_languages(practice),
            memory_limit=practice.memory_limit,
            time_limit=practice.time_limit,
            max_threads=practice.max_threads,
            command_line_args=practice.command_line_args,
            network=practice.network,
            allow_multi_file=practice.allow_multi_file,
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
