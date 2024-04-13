from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends
from starlette import status

from app.schemas import Language as LanguageSchema
from app.config.languages import LANGUAGES, ARCHIVED, Language

router = APIRouter(
    prefix='/language',
    tags=['Language']
)


@router.get(
    path='',
    response_model=list[LanguageSchema],
    status_code=status.HTTP_200_OK,
)
async def get_languages():
    return [
        LanguageSchema(id=lang.id, name=lang.name)
        for lang in LANGUAGES.values()
        if lang.id not in ARCHIVED.keys()
    ]
