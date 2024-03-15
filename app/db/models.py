from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, LargeBinary, ForeignKey

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    ...


class Participation(Base):
    __tablename__ = 'participation'
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'), primary_key=True)
    course_id: Mapped[UUID] = mapped_column(ForeignKey('course.id'), primary_key=True)


class User(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    is_teacher: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(200))
    email: Mapped[str] = mapped_column(String(50))
    courses: Mapped["Course"] = relationship(
        secondary=Participation.__table__, back_populates='participants',
    )


class Course(Base):
    __tablename__ = 'course'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column()
    participants: Mapped[List[User]] = relationship(
        secondary=Participation.__table__, back_populates='courses',
        lazy='selectin',
    )
    practices: Mapped["Practice"] = relationship(back_populates='course')


class Practice(Base):
    __tablename__ = 'practice'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    deadline: Mapped[datetime] = mapped_column()
    soft_deadline: Mapped[datetime] = mapped_column()
    course_id: Mapped[UUID] = mapped_column(ForeignKey('course.id'))
    practice_no: Mapped[int] = mapped_column()
    course: Mapped["Course"] = relationship(back_populates='practices')
