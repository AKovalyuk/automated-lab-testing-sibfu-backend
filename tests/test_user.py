import base64

import pytest
from sqlalchemy import select

from app.db.models import User
from app.utils import authenticate, create_user
from app.config import settings


@pytest.fixture
async def user_fixture(session) -> User:
    new_user = await create_user(
        session=session,
        password='123',
        username='username',
        display_name='Username',
        is_teacher=False,
        is_admin=False,
        email='example@mail.ru',
    )
    yield new_user
    await session.delete(new_user)
    await session.commit()


async def test_create_user(session, user_fixture):
    assert (await session.scalar(select(User).where(User.username == 'username'))).username == 'username'


@pytest.mark.parametrize(
    "username,password,excepted",
    [
        ('username', '123', 'username'),  # Positive
        ('username', '12345', None),  # Wrong password
        ('not-exists', '123', None),  # User not exists
    ]
)
async def test_authenticate_user(session, user_fixture, password, username, excepted):
    user = await authenticate(username=username, password=password, session=session)
    if excepted is None:
        assert user is None
    else:
        assert user.username == excepted


@pytest.mark.parametrize(
    "username,password,excepted_status_code",
    [
        ('username', '123', 200),  # Positive
        ('username', '12345', 401),  # Wrong password
        ('not-exists', '123', 401),  # User not exists
    ]
)
async def test_authenticate_user_api(client, user_fixture, password, username, excepted_status_code):
    response = await client.get(
        url=f'{settings.PATH_PREFIX}/user/{user_fixture.id}',
        headers={
            'Authorization': f'Basic {base64.b64encode(f"{username}:{password}".encode()).decode()}'
        }
    )
    assert response.status_code == excepted_status_code


@pytest.mark.parametrize(
    'header_value',
    [
        'bad_header',  # No basic
        'Basic ',  # No data
        'Basic',  # No data
        'Basic ----',  # No base64
        f'Basic {base64.b64encode(f"bad_data".encode()).decode()}',  # Bad data format
        f'Basic {base64.b64encode(f"bad:x:data".encode()).decode()}',  # Bad data format
        f'Token {base64.b64encode(f"bad:data".encode()).decode()}',  # Bad prefix
    ]
)
async def test_authenticate_user_bad_header_api(client, user_fixture, header_value):
    response = await client.get(
        url=f'{settings.PATH_PREFIX}/user/{user_fixture.id}',
        headers={
            'Authorization': header_value,
        }
    )
    assert response.status_code == 400


async def test_register_user(client, session):
    data = {
        'username': 'abcd',
        'display_name': 'Petya',
        'is_teacher': False,
        'email': 'user@example.com',
    }
    response = await client.post(
        url=f'{settings.PATH_PREFIX}/registration',
        json=data | {'password': '123'}
    )
    assert response.status_code == 200
    user_in_db = await session.scalar(select(User).filter(User.username == data['username']))
    for field in data:
        assert getattr(user_in_db, field) == data[field]


async def test_duplicate_username(client, session):
    data1 = {
        'username': 'abcd',
        'display_name': 'Petya',
        'is_teacher': False,
        'email': 'user1@example.com',
        'password': '123',
    }
    data2 = {
        'username': 'abcd',
        'display_name': 'Petya',
        'is_teacher': False,
        'email': 'user2@example.com',
        'password': '123',
    }
    response = await client.post(
        url=f'{settings.PATH_PREFIX}/registration',
        json=data1,
    )
    assert response.status_code == 200
    response = await client.post(
        url=f'{settings.PATH_PREFIX}/registration',
        json=data2,
    )
    assert response.status_code == 409


async def test_duplicate_email(client, session):
    data1 = {
        'username': 'abcd',
        'display_name': 'Petya',
        'is_teacher': False,
        'email': 'user@example.com',
        'password': '123',
    }
    data2 = {
        'username': 'abcde',
        'display_name': 'Petya',
        'is_teacher': False,
        'email': 'user@example.com',
        'password': '123',
    }
    response = await client.post(
        url=f'{settings.PATH_PREFIX}/registration',
        json=data1,
    )
    assert response.status_code == 200
    response = await client.post(
        url=f'{settings.PATH_PREFIX}/registration',
        json=data2,
    )
    assert response.status_code == 409
