from uuid import UUID

from pydantic import BaseModel, Field


class CourseIn(BaseModel):
    name: str = Field(max_length=100)
    description: str


class CourseOut(CourseIn):
    id: UUID
