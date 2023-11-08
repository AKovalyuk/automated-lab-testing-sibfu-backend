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
