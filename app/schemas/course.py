from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class CourseIn(BaseModel):
    name: str = Field(max_length=100)
    description: str
    image_id: UUID | None = None


class CourseOut(CourseIn):
    id: UUID


class ParticipationIn(BaseModel):
    user_id: UUID
    status: Literal[
        "approve",
        "remove",
    ]


class ParticipationOut(BaseModel):
    username: str
    display_name: str
    email: str
    is_teacher: bool
    is_request: bool

    model_config = ConfigDict(from_attributes=True)


class Summary(BaseModel):
    task_id: UUID
    task_name: str
    practice_id: UUID
    practice_name: str
    username: str
    display_name: str
    total_tests: int
    best_tests_passed: int
    best_attempt_time: datetime
    last_attempt_time: datetime
    attempt_count: int
    attempt_count_before_best: int
