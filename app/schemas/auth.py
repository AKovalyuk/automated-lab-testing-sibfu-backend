from datetime import datetime

from pydantic import BaseModel, Field


class AuthenticationIn(BaseModel):
    username: str = Field(max_length=25)
    password: str


class AuthenticationOut(BaseModel):
    token: str


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class RegistrationRequest(BaseModel):
    username: str
    display_name: str
    email: str
    reg_time: datetime
