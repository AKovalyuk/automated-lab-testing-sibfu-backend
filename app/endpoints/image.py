from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, status, File

from app.utils.file_storage import LocalFileStorage
from app.schemas import ImageOut


router = APIRouter(
    prefix='',
    tags=['Image'],
)


@router.post(
    path='/image',
    status_code=status.HTTP_200_OK,
    response_model=ImageOut,
)
async def create_image(file: Annotated[bytes, File()]):
    file_storage = LocalFileStorage.get_storage("images")
    ident = str(uuid4())
    await file_storage.save_bytes(ident, file)
    return ImageOut(id=ident)
