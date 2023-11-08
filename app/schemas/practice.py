from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Language(BaseModel):
    id: int
    name: str


class PracticeIn(BaseModel):
    deadline: datetime
    deadline_type: Literal['soft', 'hard']
    name: str = Field(max_length=100)
    task_id: UUID
    languages: list[int]  # available lang ids


class PracticeOut(BaseModel):
    id: UUID
    deadline: datetime
    deadline_type: Literal['soft', 'hard']
    name: str = Field(max_length=100)
    task_id: UUID
    languages: list[Language]
