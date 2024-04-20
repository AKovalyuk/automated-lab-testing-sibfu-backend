from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from .language import Language
from ..db import SubmissionStatus


class AttemptIn(BaseModel):
    source_code: str
    language_id: int


class AttemptOut(BaseModel):
    id: UUID
    meta: dict
    sent_time: datetime
    author_id: int
    practice_id: int
    passed_count: int
    total_tests: int
    status: SubmissionStatus
