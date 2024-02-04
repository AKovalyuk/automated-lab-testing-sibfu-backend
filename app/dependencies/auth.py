from dataclasses import dataclass
from typing import Annotated, Optional
from base64 import b64decode

from fastapi import Header, HTTPException, status

from app.db.models import User


def auth_dependency(authorization: Annotated[str, Header()]) -> Optional[User]:
    try:
        username, password = b64decode(authorization).decode(encoding='utf-8').split(':')
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return authenticate_user
