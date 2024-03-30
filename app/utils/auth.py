from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from app.db.models import User


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


async def authenticate(username: str, password: str, session: AsyncSession) -> User | None:
    probably_user = await session.scalar(select(User).filter_by(username=username))
    if probably_user and verify_password(password, probably_user.password_hash):
        return probably_user


async def create_user(password: str, session: AsyncSession, **kwargs) -> User:
    user = User(password_hash=hash_password(password), **kwargs)
    session.add(user)
    await session.commit()
    return user


async def create_user_with_hashed_password(
        password_hash: bytes,
        session: AsyncSession,
        **kwargs
) -> User:
    user = User(password_hash=password_hash, **kwargs)
    session.add(user)
    await session.commit()
    return user
