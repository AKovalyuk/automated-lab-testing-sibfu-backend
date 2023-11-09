from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CourseIn(BaseModel):
    name: str = Field(max_length=100)
    description: str


class CourseOut(CourseIn):
    id: UUID


class ParticipationIn(BaseModel):
    id: UUID
    status: Literal[
        "participant",
        "admin",
        "requestor",
    ]


class ParticipationOut(ParticipationIn):
    username: str
    display_name: str
    email: str


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
