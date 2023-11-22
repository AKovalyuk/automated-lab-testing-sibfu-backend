from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(max_length=25)
    display_name: str = Field(max_length=50)
    is_teacher: bool
    email: EmailStr


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID
