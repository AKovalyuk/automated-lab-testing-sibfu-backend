from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Path, Body, Depends
from starlette import status

from app.schemas.task import TaskOut, TaskIn
from app.dependencies.pagination import pagination_dependency, Pagination


router = APIRouter(
    prefix='/task',
    tags=['Task'],
)


@router.get(
    path='/{task_id}',
    response_model=TaskOut,
    status_code=status.HTTP_200_OK,
)
async def get_task(task_id: Annotated[UUID, Path()]) -> TaskOut:
    """
    Get task by id
    """
    pass


@router.get(
    path='/',
    response_model=list[TaskOut],
    status_code=status.HTTP_200_OK,
)
async def get_tasks(
        pagination: Annotated[Pagination, Depends(pagination_dependency)]
) -> list[TaskOut]:
    """
    List tasks with pagination
    """
    pass


@router.post(
    path='/',
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(task_data: Annotated[TaskIn, Body()]) -> TaskOut:
    """
    Endpoint for task creation
    """
    pass


@router.patch(
    path='/{task_id}',
    response_model=TaskOut,
    status_code=status.HTTP_200_OK,
)
async def edit_task(
        task_id: Annotated[UUID, Path()],
        task_data: Annotated[TaskIn, Body()]
) -> TaskOut:
    """
    Endpoint for task edit
    """
    pass


@router.delete(
    path='/{task_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(task_id: Annotated[UUID, Path()]):
    """
    Delete task endpoint
    """
    pass

