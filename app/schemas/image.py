from uuid import UUID

from pydantic import BaseModel


class ImageOut(BaseModel):
    id: UUID
