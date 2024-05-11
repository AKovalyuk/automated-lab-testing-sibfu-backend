from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from .abstract import AbstractFileStorage


class LocalFileStorage(AbstractFileStorage):
    # TODO Chunk-by-chunk read

    def __init__(self, storage_name: str):
        self.storage_name = storage_name
        self.path = Path("")

    @classmethod
    def get_storage(cls, storage_name: str) -> "AbstractFileStorage":
        return cls(storage_name)

    async def save_bytes(self, ident: str, data: bytes):
        with open(self.path / ident, "wb") as file:
            file.write(data)

    async def load_bytes(self, ident: str) -> bytes:
        with open(self.path / ident, "rb") as file:
            return file.read()

    async def save_stream(self, ident: str, stream: BinaryIO):
        await self.save_bytes(ident, stream.read())

    async def load_stream(self, ident: str) -> BinaryIO:
        with open(self.path / ident, "rb") as file:
            return BytesIO(file.read())

    async def delete_file(self, ident: str) -> None:
        (self.path / ident).unlink()
