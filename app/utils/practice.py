from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Participation, Course, User, Practice


async def practice_has_read_permission(
        user: User,
        practice: Practice,
        session: AsyncSession
) -> bool:
    participation = await session.scalar(
        select(Participation).
        where(
            Participation.user_id == user.id,
            Participation.course_id == practice.course_id
        )
    )
    return participation is not None and not participation.is_request


async def practice_has_write_permission(
        user: User,
        practice: Practice,
        session: AsyncSession
) -> bool:
    return await practice_has_read_permission(user, practice, session) and user.is_teacher
