from uuid import uuid4
from time import time

import pytest
from sqlalchemy import select

from app.config import settings
from app.db import Course, Participation
from tests.utils import create_test_user, create_test_course, get_user_authorization_header


async def test_get_course_by_id_exists_participated(client, session):
    user, password = await create_test_user(session)
    new_course = await create_test_course(session)
    session.add(Participation(user_id=user.id, course_id=new_course.id))
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{new_course.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(new_course.id)
    assert response.json()["name"] == new_course.name


async def test_get_course_by_id_not_exists(client, session):
    user, password = await create_test_user(session)
    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{uuid4()}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 404


async def test_get_course_by_id_exists_not_participated(client, session):
    user, password = await create_test_user(session)

    new_course = await create_test_course(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{new_course.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 403


async def test_get_course_by_id_exists_teacher(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    new_course = await create_test_course(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{new_course.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(new_course.id)
    assert response.json()["name"] == new_course.name


async def test_get_courses_0_participated(client, session):
    courses = [await create_test_course(session) for _ in range(3)]
    user, password = await create_test_user(session)

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/",
        headers=get_user_authorization_header(user, password),
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
        headers=get_user_authorization_header(user, password),
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
        headers=get_user_authorization_header(user, password),
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
        headers=get_user_authorization_header(user, password),
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
        headers=get_user_authorization_header(user, password),
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
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code in (400, 403)


async def test_update_course_by_teacher_participant(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(course_id=course.id, user_id=user.id)
    session.add(participation)
    await session.commit()

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/course/{course.id}",
        headers=get_user_authorization_header(user, password),
        json={
            "name": "Test Course",
            "description": "...",
        },
    )
    assert response.status_code == 200


async def test_update_course_by_teacher_not_participant(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/course/{course.id}",
        headers=get_user_authorization_header(user, password),
        json={
            "name": "Test Course",
            "description": "...",
        },
    )
    assert response.status_code == 403


async def test_update_course_by_student_participant(client, session):
    user, password = await create_test_user(session, is_teacher=False)
    course = await create_test_course(session)
    participation = Participation(course_id=course.id, user_id=user.id)
    session.add(participation)
    await session.commit()

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/course/{course.id}",
        headers=get_user_authorization_header(user, password),
        json={
            "name": "Test Course",
            "description": "...",
        },
    )
    assert response.status_code == 403


async def test_update_course_not_exists(client, session):
    user, password = await create_test_user(session, is_teacher=True)

    response = await client.put(
        url=f"{settings.PATH_PREFIX}/course/{uuid4()}",
        headers=get_user_authorization_header(user, password),
        json={
            "name": "Test Course",
            "description": "...",
        },
    )
    assert response.status_code == 404


async def test_delete_course_ok(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)
    participation = Participation(course_id=course.id, user_id=user.id)
    session.add(participation)
    await session.commit()
    course_id = course.id

    response = await client.delete(
        url=f"{settings.PATH_PREFIX}/course/{course.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code in (200, 204)
    assert list(await session.execute(
        select(Course.id).where(Course.id == course_id)
    )).__len__() == 0
    assert list(await session.execute(
        select(Participation.course_id).
        where(Participation.course_id == course_id).
        where(Participation.user_id == user.id)
    )).__len__() == 0


async def test_delete_course_no_permission(client, session):
    user, password = await create_test_user(session, is_teacher=False)
    course = await create_test_course(session)
    participation = Participation(course_id=course.id, user_id=user.id)
    session.add(participation)
    await session.commit()

    response = await client.delete(
        url=f"{settings.PATH_PREFIX}/course/{course.id}",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 403


async def test_participation_request_once(client, session):
    user, password = await create_test_user(session, is_teacher=False)
    course = await create_test_course(session)

    response = await client.patch(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/participation",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert await session.scalar(
        select(Participation).
        where(Participation.course_id == course.id).
        where(Participation.user_id == user.id)
    )


async def test_participation_request_multiple(client, session):
    user, password = await create_test_user(session, is_teacher=False)
    course = await create_test_course(session)

    for _ in range(3):
        response = await client.patch(
            url=f"{settings.PATH_PREFIX}/course/{course.id}/participation",
            headers=get_user_authorization_header(user, password),
        )
        assert response.status_code == 200
    participation_object = await session.scalar(
        select(Participation).
        where(Participation.course_id == course.id).
        where(Participation.user_id == user.id)
    )
    assert participation_object.is_request


@pytest.mark.parametrize(
    "page, page_size, request_count, participant_count, excepted_count",
    [
        (1, 10, 3, 5, 8),
        (2, 10, 3, 5, 0),
        (4, 3, 0, 10, 1),
    ]

)
async def test_get_participation(
        client, session,
        page, page_size, request_count, participant_count, excepted_count
):
    course = await create_test_course(session)
    users = []
    teacher_user, teacher_password = await create_test_user(session, is_teacher=True)
    for i in range(request_count + participant_count):
        user, password = await create_test_user(session)
        users.append((user, password))
        session.add(
            Participation(user_id=user.id, course_id=course.id, is_request=i < request_count)
        )
    await session.commit()

    response = await client.get(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/participation",
        params={"page": page, "size": page_size},
        headers=get_user_authorization_header(teacher_user, teacher_password),
    )
    assert len(response.json()) == excepted_count


async def test_change_update_participation_not_found(client, session):
    user, password = await create_test_user(session, is_teacher=True)
    course = await create_test_course(session)

    response = await client.patch(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/participation",
        headers=get_user_authorization_header(user, password),
        json=[
            {"user_id": str(uuid4()), "status": "approve"},
            {"user_id": str(uuid4()), "status": "remove"},
        ]
    )
    assert response.status_code == 200


async def test_change_update_participation_cross_table(client, session):
    participants = [await create_test_user(session) for _ in range(4)]
    course = await create_test_course(session)
    teacher, teacher_password = await create_test_user(session, is_teacher=True)
    participation = Participation(user_id=teacher.id, course_id=course.id)
    participations = [
        Participation(
            user_id=participants[i][0].id,
            course_id=course.id,
            is_request=i < 2,
        )
        for i in range(4)
    ]
    session.add_all(participations + [participation])
    await session.commit()

    response = await client.patch(
        url=f"{settings.PATH_PREFIX}/course/{course.id}/participation_update",
        headers=get_user_authorization_header(teacher, teacher_password),
        json=[
            {
                "user_id": str(participants[i][0].id), "status":
                "approve" if i % 2 == 0 else "remove"
            }
            for i in range(4)
        ]
    )
    assert response.status_code == 200
    for i, t in enumerate(participants):
        user, _ = t
        if i % 2 == 0:
            assert not (await session.execute(
                select(Participation.is_request).
                where(Participation.course_id == course.id).
                where(Participation.user_id == user.id)
            )).scalar_one_or_none()
        else:
            assert (await session.execute(
                select(Participation).
                where(Participation.course_id == course.id).
                where(Participation.user_id == user.id)
            )).scalar_one_or_none() is None
