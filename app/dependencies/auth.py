from typing import Annotated, Optional
from base64 import b64decode

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, HTTPException, status, Depends

from app.db.models import User
from app.utils.auth import authenticate
from app.db.connection import get_session


async def auth_dependency(
        authorization: Annotated[str, Header()],
        session: Annotated[AsyncSession, Depends(get_session)],
) -> Optional[User]:
    try:
        auth_data = authorization.removeprefix('Basic ')
        username, password = b64decode(auth_data).decode(encoding='utf-8').split(':')
    except Exception as e:  # TODO Exceptions types
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Bad authorization header: {e}'
        )
    else:
        user = await authenticate(username=username, password=password, session=session)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user
