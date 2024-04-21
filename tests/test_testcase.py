from datetime import datetime
from uuid import uuid4

from sqlalchemy import select

from app.config import settings
from app.db import Practice, Participation, TestCase
from tests.utils import (
    create_test_user,
    create_test_course,
    create_test_practice,
    add_testcase_to_practice,
    get_user_authorization_header,
)


async def test_get_testcase(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    practice = await create_test_practice(session, course, user)
    testcase = TestCase(input="1 2\n", excepted="3\n", hidden=True, practice_id=practice.id)
    session.add(testcase)
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/testcase/{testcase.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert response.json()["id"] == testcase.id


async def test_get_testcases(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    practice = await create_test_practice(session, course, user)
    testcases = [
        TestCase(input="1 2\n", excepted="3\n", hidden=True, practice_id=practice.id)
        for _ in range(4)
    ]
    session.add_all(testcases)
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}/testcase",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert len(response.json()) == 4


async def test_delete_testcase(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    practice = await create_test_practice(session, course, user)
    testcase = TestCase(input="1 2\n", excepted="3\n", hidden=True, practice_id=practice.id)
    session.add(testcase)
    await session.commit()

    response = await client.delete(
        url=f"{settings.PATH_PREFIX}/testcase/{testcase.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code in [200, 204]
    assert await session.scalar(
        select(TestCase).
        where(TestCase.practice_id == practice.id)
    ) is None


async def test_create_testcase(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    practice = await create_test_practice(session, course, user)

    testcase_data = {
        "input": "1 2\n",
        "excepted": "3\n",
        "hidden": True,
    }

    response = await client.post(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}/testcase",
        headers=get_user_authorization_header(user, password),
        json=testcase_data,
    )
    assert response.status_code in [200, 201]
    assert response.json().items() >= testcase_data.items()


async def test_update_testcase(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    practice = await create_test_practice(session, course, user)
    testcase = TestCase(input="1 2\n", excepted="3\n", hidden=True, practice_id=practice.id)
    session.add(testcase)
    await session.commit()

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/testcase/{testcase.id}",
        headers=get_user_authorization_header(user, password),
        json={
            "input": "aaa\n",
            "excepted": "bbb\n",
            "hidden": True,
        }
    )
    assert response.status_code == 200
