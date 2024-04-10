from datetime import datetime
from typing import List
from unittest import TestCase
from uuid import UUID, uuid4

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,
)
from sqlalchemy import (
    String,
    LargeBinary,
    ForeignKey,
    UniqueConstraint,
    ARRAY,
)


class Base(DeclarativeBase):
    ...


class Participation(Base):
    __tablename__ = 'participation'
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete="CASCADE"), primary_key=True,
    )
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey('course.id', ondelete="CASCADE"), primary_key=True,
    )
    is_request: Mapped[bool] = mapped_column(default=False)
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="unique_participation"),
    )


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
    description: Mapped[str] = mapped_column()

    deadline: Mapped[datetime] = mapped_column()
    soft_deadline: Mapped[datetime] = mapped_column()

    course_id: Mapped[UUID] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates='practices')
    author_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))

    testcases: Mapped[list["TestCase"]] = relationship(back_populates='practice')


class TestCase(Base):
    __tablename__ = 'testcase'
    id: Mapped[int] = mapped_column(primary_key=True)
    input: Mapped[UUID]
    excepted: Mapped[UUID]
    hidden: Mapped[bool] = mapped_column(default=True)

    practice_id: Mapped[UUID] = mapped_column(ForeignKey('practice.id'))
    practice: Mapped["Practice"] = relationship(back_populates='testcases')
