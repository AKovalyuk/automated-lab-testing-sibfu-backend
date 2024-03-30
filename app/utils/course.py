from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import Course, User, Participation


async def is_participant(
        course: Course,
        user: User,
        session: AsyncSession
) -> bool:
    participation = (await session.execute(
        select(Participation).where(
            Participation.course_id == course.id,
            Participation.user_id == user.id,
            Participation.is_request == False,
        )
    )).scalar()
    return bool(participation) and not participation.is_request


class CoursePermission(Enum):
    NONE = 1
    READ = 2
    WRITE = 3


async def get_course_permission(
        course: Course,
        user: User,
        session: AsyncSession
) -> CoursePermission:
    # Allow edit course only for teacher participate in course
    user_is_participant = await is_participant(course, user, session)
    if user.is_teacher and user_is_participant:
        return CoursePermission.WRITE
    # Allow read course only for any teacher or course participants
    if user.is_teacher or user_is_participant:
        return CoursePermission.READ
    return CoursePermission.NONE
