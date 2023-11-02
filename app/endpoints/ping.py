from fastapi import APIRouter


router = APIRouter(prefix='/health_check')


@router.get('/ping')
async def ping():
    return {'message': 'Application works'}
