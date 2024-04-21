from pydantic import BaseModel, ConfigDict


class TestCaseIn(BaseModel):
    input: str
    excepted: str
    hidden: bool = True


class TestCaseOutBrief(BaseModel):
    id: int
    hidden: bool

    model_config = ConfigDict(from_attributes=True)


class TestCaseOut(TestCaseIn):
    id: int

    model_config = ConfigDict(from_attributes=True)
