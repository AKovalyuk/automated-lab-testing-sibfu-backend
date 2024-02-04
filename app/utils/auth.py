from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from app.db.models import User


async def authenticate(username: str, password: str, session: AsyncSession) -> User | None:
    probably_user = await session.scalar(select(User).filter_by(username=username))
    if probably_user and bcrypt.checkpw(password.encode(), probably_user.password_hash):
        return probably_user


async def create_user(password: str, session: AsyncSession, **kwargs) -> User:
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user = User(password_hash=password_hash, **kwargs)
    session.add(user)
    await session.commit()
    return user
