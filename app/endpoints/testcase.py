from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status, Depends, Path, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db import User, get_session, Practice, TestCase
from app.dependencies import auth_dependency
from app.schemas import TestCaseIn, TestCaseOut, TestCaseOutBrief


router = APIRouter(
    prefix="",
    tags=["Testcase"],
)


@router.get(
    path="/practice/{practice_id}/testcase",
    response_model=list[TestCaseOutBrief],
    status_code=status.HTTP_200_OK,
)
async def get_testcases(
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        practice_id: Annotated[UUID, Path()],
) -> list[TestCaseOutBrief]:
    practice = await session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    testcases = await session.scalars(
        select(TestCase).
        where(TestCase.practice_id == practice.id)
    )
    return [
        TestCaseOutBrief.model_validate(testcase)
        for testcase in testcases
    ]


@router.get(
    path="/testcase/{testcase_id}",
    response_model=TestCaseOut,
    status_code=status.HTTP_200_OK,
)
async def get_testcases(
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        testcase_id: Annotated[int, Path()],
) -> TestCaseOut:
    testcase = await session.get(TestCase, testcase_id)
    if not testcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return TestCaseOut.model_validate(testcase)


@router.delete(
    path="/testcase/{testcase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_testcase(
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        testcase_id: Annotated[int, Path()],
):
    testcase = await session.get(TestCase, testcase_id)
    if not testcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await session.delete(testcase)
    await session.commit()


@router.post(
    path="/practice/{practice_id}/testcase",
    status_code=status.HTTP_201_CREATED,
    response_model=TestCaseOut,
)
async def create_testcase(
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        practice_id: Annotated[UUID, Path()],
        testcase_data: Annotated[TestCaseIn, Body()],
) -> TestCaseOut:
    practice = await session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    testcase = TestCase(
        input=testcase_data.input,
        excepted=testcase_data.excepted,
        hidden=testcase_data.hidden,
        practice_id=practice.id,
    )
    session.add(testcase)
    await session.commit()
    return TestCaseOut.model_validate(testcase)


@router.put(
    path="/testcase/{testcase_id}",
    status_code=status.HTTP_200_OK,
    response_model=TestCaseOut,
)
async def update_testcase(
        user: Annotated[User, Depends(auth_dependency)],
        session: Annotated[AsyncSession, Depends(get_session)],
        testcase_data: Annotated[TestCaseIn, Body()],
        testcase_id: Annotated[int, Path()],
) -> TestCaseOut:
    testcase = await session.get(TestCase, testcase_id)
    if not testcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    for k, v in testcase_data.model_dump():
        setattr(testcase, k, v)
    await session.commit()
    return TestCaseOut.model_validate(testcase)
