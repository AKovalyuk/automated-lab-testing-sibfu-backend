from uuid import UUID
from datetime import datetime
from typing import Literal
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict


class ParticipationStatus(StrEnum):
    PARTICIPANT = "PARTICIPANT"
    REQUESTOR = "REQUESTOR"
    NONE = "NONE"


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
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CourseSearchResult(CourseOut):
    participation_status: ParticipationStatus


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
