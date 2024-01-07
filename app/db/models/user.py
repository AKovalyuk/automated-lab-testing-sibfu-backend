from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    display_name: Mapped[str] = mapped_column(String(100))
    is_teacher: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(50))
