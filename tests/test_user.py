import pytest
from sqlalchemy import select
from pytest import fixture

from app.db.models import User
from app.utils import authenticate, create_user


@pytest.fixture
async def user_fixture(session):
    new_user = await create_user(
        session=session,
        password='123',
        username='username',
        display_name='Username',
        is_teacher=False,
        is_admin=False,
        email='example@mail.ru',
    )
    yield
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
