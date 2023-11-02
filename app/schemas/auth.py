from pydantic import BaseModel, Field


class AuthenticationIn(BaseModel):
    username: str = Field(max_length=25)
    password: str


class AuthenticationOut(BaseModel):
    token: str
