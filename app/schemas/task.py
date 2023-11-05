from uuid import UUID

from pydantic import BaseModel, Field


class Test(BaseModel):
    stdin: str
    stdout: str


class TaskIn(BaseModel):
    name: str = Field(max_length=100)
    tests: list[Test]


class TaskOut(BaseModel):
    name: str = Field(max_length=100)
    description: UUID
    author: UUID
    tests: list[Test]
