import base64

from app.db import User


def get_user_authorization_header(user: User, password: str) -> str:
    return f'Basic {base64.b64encode(f"{user.username}:{password}".encode()).decode()}'
