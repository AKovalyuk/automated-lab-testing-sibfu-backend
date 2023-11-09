from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends
from starlette import status

from app.schemas import Language

router = APIRouter(
    prefix='/language',
    tags=['Language']
)


@router.get(
    path='/',
    response_model=list[Language],
    status_code=status.HTTP_200_OK,
)
async def get_languages():
    """
    Get all available languages
    """
    pass
