from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from .language import Language


class PracticeIn(BaseModel):
    name: str = Field(max_length=100)
    description: str
    deadline: datetime
    soft_deadline: datetime
    # languages: list[Language]


class PracticeOut(BaseModel):
    id: UUID
    name: str = Field(max_length=100)
    description: str
    deadline: datetime
    soft_deadline: datetime
    course_id: UUID
    author_id: UUID
    # languages: list[Language] TODO

    model_config = ConfigDict(from_attributes=True)
