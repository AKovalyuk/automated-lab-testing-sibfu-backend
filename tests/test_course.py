from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db import User, Course, Participation
from app.utils import create_user, get_user_authorization_header


async def create_test_user(session: AsyncSession, is_teacher=False):
    password = "123"
    user = await create_user(
        session=session,
        password=password,
        username="test_user",
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


async def test_get_course_by_id_exists_participated(client, session):
    user, password = await create_test_user(session)
    new_course = await create_test_course(session)
    session.add(Participation(user_id=user.id, course_id=new_course.id))
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{new_course.id}",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(new_course.id)
    assert response.json()["name"] == new_course.name


async def test_get_course_by_id_not_exists(client, session):
    user, password = await create_test_user(session)
    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{uuid4()}",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 404


async def test_get_course_by_id_exists_not_participated(client, session):
    user, password = await create_test_user(session)

    new_course = await create_test_course(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{new_course.id}",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 403


async def test_get_course_by_id_exists_teacher(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    new_course = await create_test_course(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{new_course.id}",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(new_course.id)
    assert response.json()["name"] == new_course.name


async def test_get_courses_0_participated(client, session):
    courses = [await create_test_course(session) for _ in range(3)]
    user, password = await create_test_user(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_courses_1_participated(client, session):
    courses = [await create_test_course(session) for _ in range(3)]
    user, password = await create_test_user(session)
    participation = Participation(user_id=user.id, course_id=courses[0].id)
    session.add(participation)
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(courses[0].id)


async def test_get_courses_many_participated(client, session):
    courses = [await create_test_course(session) for _ in range(4)]
    user, password = await create_test_user(session)
    session.add_all([Participation(user_id=user.id, course_id=courses[i].id) for i in range(2)])
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == str(courses[0].id)
    assert response.json()[1]["id"] == str(courses[1].id)


async def test_get_courses_many_teacher(client, session):
    courses = [await create_test_course(session) for _ in range(4)]
    user, password = await create_test_user(session, is_teacher=True)
    session.add_all([Participation(user_id=user.id, course_id=courses[i].id) for i in range(2)])
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/",
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 4


async def test_create_course_by_teacher(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    response = await client.post(
        url=f"{settings.PATH_PREFIX}/course/",
        json={
            "name": "Test Course",
            "description": "...",
        },
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code in (200, 201)
    course_id = response.json()["id"]
    assert await session.get(Course, course_id)
    assert len(list(await session.scalars(select(Course)))) == 1
    assert len(list(await session.scalars(select(Participation)))) == 1
    participation = await session.scalar(select(Participation))
    assert participation.user_id == user.id and str(participation.course_id) == course_id


async def test_create_course_by_student(client, session):
    user, password = await create_test_user(session, is_teacher=False)
    response = await client.post(
        url=f"{settings.PATH_PREFIX}/course/",
        json={
            "name": "Test Course",
            "description": "...",
        },
        headers={
            "Authorization": get_user_authorization_header(user, password),
        }
    )
    assert response.status_code in (400, 403)
