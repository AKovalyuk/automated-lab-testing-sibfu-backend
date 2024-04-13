from datetime import datetime
from time import time
from uuid import uuid4
import base64

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.utils import create_user
from app.db import Course, Practice, TestCase


def get_user_authorization_header(user: User, password: str) -> dict[str, str]:
    return {
        'Authorization': f'Basic {base64.b64encode(f"{user.username}:{password}".encode()).decode()}'
    }


async def create_test_user(session: AsyncSession, is_teacher=False):
    password = "123"
    user = await create_user(
        session=session,
        password=password,
        username=f"test_user_{int(time() * 1000)}",
        display_name="test_display_name",
        is_teacher=is_teacher,
        is_admin=False,
        email="a@mail.com",
    )
    return user, password


async def create_test_course(session: AsyncSession):
    new_course = Course(name="Test course", description="...")
    session.add(new_course)
    await session.commit()
    return new_course


async def create_test_practice(session: AsyncSession, course: Course, author: User):
    new_practice = Practice(
        name="Test practice",
        description="...",
        deadline=datetime.now(),
        soft_deadline=datetime.now(),
        course_id=course.id,
        author_id=author.id,
    )
    session.add(new_practice)
    await session.commit()
    return new_practice


async def add_testcase_to_practice(session: AsyncSession, practice: Practice, hidden: bool):
    testcase = TestCase(
        input=uuid4(),
        excepted=uuid4(),
        hidden=hidden,
        practice=practice,
    )
    session.add(testcase)
    await session.commit()
    return testcase

