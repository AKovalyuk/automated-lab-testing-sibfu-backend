from fastapi import APIRouter, Request
from starlette import status

from app.schemas import CallbackServerRequest


router = APIRouter(
    prefix=''
)


@router.put(
    path='/',
    status_code=status.HTTP_200_OK,
)
async def callback(message: CallbackServerRequest):
    print(message)
