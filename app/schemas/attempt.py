from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from .language import Language


class AttemptIn(BaseModel):
    pass


class AttemptOut(BaseModel):
    id: UUID
    status: Literal[
        "Wrong answer",
        "Accepted",
        "Compilation error",
    ]
    passed_count: int
    total_tests: int
    linter_score: int | None
    language: Language
    sent_time: datetime
