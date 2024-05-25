from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .language import Language
from ..db import SubmissionStatus


class AttemptIn(BaseModel):
    source_code: str
    language_id: int


class AttemptOut(BaseModel):
    id: UUID
    meta: dict
    sent_time: datetime
    author_id: UUID
    practice_id: UUID
    # passed_count: int
    # total_tests: int
    status: SubmissionStatus

    model_config = ConfigDict(from_attributes=True)
