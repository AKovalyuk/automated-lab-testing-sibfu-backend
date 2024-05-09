from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .testcase import TestCaseIn, TestCaseOut
from .language import Language


class PracticeIn(BaseModel):
    name: str = Field(max_length=100)
    description: str
    deadline: datetime
    soft_deadline: datetime
    languages: list[int]

    memory_limit: int = Field(ge=1)
    time_limit: int = Field(ge=1)
    max_threads: int = Field(ge=1)
    command_line_args: str = Field(max_length=512)
    network: bool
    allow_multi_file: bool

    testcases: list[TestCaseIn] | None


class PracticeOut(BaseModel):
    id: UUID
    name: str = Field(max_length=100)
    description: str
    deadline: datetime
    soft_deadline: datetime
    course_id: UUID
    author_id: UUID
    languages: list[Language] | None

    memory_limit: int = Field(ge=1)
    time_limit: int = Field(ge=1)
    max_threads: int = Field(ge=1)
    command_line_args: str = Field(max_length=512)
    network: bool
    allow_multi_file: bool

    testcases: list[TestCaseOut] | None

    model_config = ConfigDict(from_attributes=True)
