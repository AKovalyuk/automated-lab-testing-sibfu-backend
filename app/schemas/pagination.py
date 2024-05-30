from typing import TypeVar, Generic

from pydantic.generics import GenericModel


T = TypeVar("T")


class PaginationResult(GenericModel, Generic[T]):
    count: int
    results: list[T]
