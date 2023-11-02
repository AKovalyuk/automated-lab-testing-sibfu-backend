from fastapi import APIRouter


router = APIRouter(prefix='/health_check')


@router.get(
    '/ping',
    tags=['Healthcheck'],
)
async def ping():
    return {'message': 'Application works'}
