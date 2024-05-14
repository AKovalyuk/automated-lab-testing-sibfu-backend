from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from enum import Enum

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
    Integer,
    JSON,
    TIMESTAMP,
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
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="author")


class Course(Base):
    __tablename__ = 'course'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column()
    image_id: Mapped[UUID] = mapped_column(nullable=True)

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

    deadline: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True))
    soft_deadline: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True))

    course_id: Mapped[UUID] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates='practices')
    author_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))
    languages: Mapped[list[int]] = mapped_column(ARRAY(Integer), server_default="{}")

    testcases: Mapped[list["TestCase"]] = relationship(back_populates='practice', lazy='joined',)
    attempts: Mapped[list["Attempt"]] = relationship(back_populates="practice")

    memory_limit: Mapped[int] = mapped_column()
    time_limit: Mapped[int] = mapped_column()
    max_threads: Mapped[int] = mapped_column(default=1)
    command_line_args: Mapped[str] = mapped_column(String(512), default="")
    network: Mapped[bool] = mapped_column()
    allow_multi_file: Mapped[bool] = mapped_column()


class TestCase(Base):
    __tablename__ = 'testcase'
    id: Mapped[int] = mapped_column(primary_key=True)
    input: Mapped[str] = mapped_column(String)
    excepted: Mapped[str] = mapped_column(String)
    hidden: Mapped[bool] = mapped_column(default=True)

    practice_id: Mapped[UUID] = mapped_column(ForeignKey('practice.id'))
    practice: Mapped["Practice"] = relationship(back_populates='testcases')


class Attempt(Base):
    __tablename__ = 'attempt'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    language_id: Mapped[int] = mapped_column()
    meta: Mapped[dict] = mapped_column(JSON)
    sent_time: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True))
    status: Mapped[str] = mapped_column(String(50))

    author_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))
    author: Mapped["User"] = relationship(back_populates="attempts")
    practice_id: Mapped[UUID] = mapped_column(ForeignKey('practice.id'))
    practice: Mapped["Practice"] = relationship(back_populates='attempts')
    submissions: Mapped[list["Submission"]] = relationship(back_populates="attempt")


class Submission(Base):
    __tablename__ = 'submission'
    token: Mapped[UUID] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50))
    time: Mapped[int] = mapped_column()
    memory: Mapped[int] = mapped_column()

    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("attempt.id"))
    attempt: Mapped["Attempt"] = relationship(back_populates="submissions")


class SubmissionStatus(Enum):
    IN_QUEUE = "IN_QUEUE"
    ACCEPTED = "ACCEPTED"
    TIME_LIMIT_EXCEED = "TIME_LIMIT_EXCEED"
    MEMORY_LIMIT_EXCEED = "MEMORY_LIMIT_EXCEED"
    WRONG_ANSWER = "WRONG_ANSWER"
    SERVICE_ERROR = "SERVICE_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"
