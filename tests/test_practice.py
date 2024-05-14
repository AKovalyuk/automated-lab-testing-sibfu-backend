from datetime import datetime
from uuid import uuid4

from sqlalchemy import select

from app.config import settings
from app.db import Practice, Participation
from tests.utils import (
    create_test_user,
    create_test_course,
    create_test_practice,
    add_testcase_to_practice,
    get_user_authorization_header,
)


async def test_get_practice(client, session):
    user, password = await create_test_user(session)
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(practice.id)


async def test_get_practice_with_tests_by_student(client, session):
    user, password = await create_test_user(session)
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)
    await add_testcase_to_practice(session, practice, True)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert response.json()["testcases"] is None


async def test_get_practice_with_tests_by_teacher(client, session):
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=teacher_user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)
    await add_testcase_to_practice(session, practice, True)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(teacher_user, teacher_password),
    )
    assert response.status_code == 200
    assert len(response.json()["testcases"]) == 1
    await session.refresh(practice)
    assert len(practice.testcases) == 1


async def test_get_practice_404(client, session):
    user, password = await create_test_user(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/practice/{uuid4()}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 404


async def test_get_practice_list(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practices = [await create_test_practice(session, course, user) for _ in range(10)]

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/practice",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert len(response.json()) == 10
    assert response.json()[0]["testcases"] is None


async def test_create_practice(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=user.id, course_id=course.id)
    session.add(participation)
    await session.commit()

    response = await client.post(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/practice",
        json={
            "name": "Test Practice",
            "description": "Test Practice",
            "deadline": datetime.now().isoformat() + 'Z',  # Check timezone ISO format
            "soft_deadline": datetime.now().isoformat(),
            "languages": [1, 2],

            "memory_limit": 128000,
            "time_limit": 500,
            "max_threads": 5,
            "command_line_args": "--help",
            "network": True,
            "allow_multi_file": False,

            "testcases": [],
        },
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code in [200, 201]
    practice: Practice = await session.get(Practice, ident=response.json()["id"])
    assert practice is not None
    assert len(practice.testcases) == 0


async def test_create_practice_with_testcases(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=user.id, course_id=course.id)
    session.add(participation)
    await session.commit()

    response = await client.post(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/practice",
        json={
            "name": "Test Practice",
            "description": "Test Practice",
            "deadline": datetime.now().isoformat(),
            "soft_deadline": datetime.now().isoformat(),
            "languages": [1, 2],

            "memory_limit": 128000,
            "time_limit": 500,
            "max_threads": 5,
            "command_line_args": "--help",
            "network": True,
            "allow_multi_file": False,

            "testcases": [
                {
                    "input": "2 + 2",
                    "excepted": "4",
                    "hidden": True,
                }
            ],
        },
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code in [200, 201]
    practice: Practice = await session.get(Practice, ident=response.json()["id"])
    assert practice is not None
    assert len(practice.testcases) == 1


async def test_delete_practice(client, session):
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=teacher_user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)

    response = await client.delete(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(teacher_user, teacher_password),
    )
    assert response.status_code == 204

    assert list(await session.execute(
        select(Practice).where(Practice.id == practice.id)
    )) == []


async def test_edit_practice(session, client):
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=teacher_user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(teacher_user, teacher_password),
        json={
            "name": "Test Practice+",
            "description": "Test Practice+",
            "deadline": datetime.now().isoformat(),
            "soft_deadline": datetime.now().isoformat(),
            "languages": [1],

            "memory_limit": 128000,
            "time_limit": 500,
            "max_threads": 5,
            "command_line_args": "--help",
            "network": True,
            "allow_multi_file": False,
            "testcases": None,
        },
    )
    await session.refresh(practice)
    assert response.status_code == 200
    assert len(practice.testcases) == 0


async def test_edit_practice_with_testcases_not_touched(session, client):
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=teacher_user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)
    await add_testcase_to_practice(session, practice, False)
    await add_testcase_to_practice(session, practice, True)

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(teacher_user, teacher_password),
        json={
            "name": "Test Practice+",
            "description": "Test Practice+",
            "deadline": datetime.now().isoformat(),
            "soft_deadline": datetime.now().isoformat(),
            "languages": [1],

            "memory_limit": 128000,
            "time_limit": 500,
            "max_threads": 5,
            "command_line_args": "--help",
            "network": True,
            "allow_multi_file": False,
            "testcases": None,
        },
    )
    await session.refresh(practice)
    assert response.status_code == 200
    assert len(practice.testcases) == 2


async def test_edit_practice_with_testcases_changed(session, client):
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(user_id=teacher_user.id, course_id=course.id)
    session.add(participation)
    await session.commit()
    practice = await create_test_practice(session, course, teacher_user)
    await add_testcase_to_practice(session, practice, False)
    await add_testcase_to_practice(session, practice, True)

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/practice/{practice.id}",
        headers=get_user_authorization_header(teacher_user, teacher_password),
        json={
            "name": "Test Practice+",
            "description": "Test Practice+",
            "deadline": datetime.now().isoformat(),
            "soft_deadline": datetime.now().isoformat(),
            "languages": [1],

            "memory_limit": 128000,
            "time_limit": 500,
            "max_threads": 5,
            "command_line_args": "--help",
            "network": True,
            "allow_multi_file": False,
            "testcases": [
                {
                    "input": "2 + 2",
                    "excepted": "4",
                    "hidden": True,
                }
            ],
        },
    )
    await session.refresh(practice)
    assert response.status_code == 200
    assert len(practice.testcases) == 1
