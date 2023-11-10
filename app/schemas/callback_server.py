from uuid import UUID

from typing import Optional

from pydantic import BaseModel


class CallbackRequestStatus(BaseModel):
    id: int
    description: str


class CallbackServerRequest(BaseModel):
    stdout: str | None
    time: float
    memory: int
    stderr: str | None
    token: UUID
    compile_output: str | None
    message: str | None
    status: CallbackRequestStatus | None
