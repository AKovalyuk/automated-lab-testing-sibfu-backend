from abc import ABC, abstractmethod
from typing import BinaryIO


class AbstractFileStorage(ABC):

    @classmethod
    @abstractmethod
    def get_storage(cls, storage_name: str) -> "AbstractFileStorage":
        ...

    @abstractmethod
    async def save_bytes(self, ident: str, data: bytes):
        ...

    @abstractmethod
    async def save_stream(self, ident: str, stream: BinaryIO):
        ...

    @abstractmethod
    async def load_bytes(self, ident: str) -> bytes:
        ...

    @abstractmethod
    async def load_stream(self, ident: str) -> BinaryIO:
        ...

    @abstractmethod
    async def delete_file(self, ident: str) -> None:
        ...
