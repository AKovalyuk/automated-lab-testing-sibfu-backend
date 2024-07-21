from argparse import Namespace
from asyncio import get_event_loop_policy
from os import environ
from types import SimpleNamespace
from typing import Union
from uuid import uuid4
from pathlib import Path

import pytest
from alembic.command import upgrade
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.__main__ import app
from app.config import settings
from app.db.connection import SessionManager


pytest_plugins = [
    'pytest_asyncio',
]
environ["ENV"] = "test"


@pytest.fixture()
def postgres() -> str:
    """
    Create temporary database for testing
    """
    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.get_db_url()
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.get_db_url_async()
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri_async: str):
    async_engine = create_async_engine(database_uri_async, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    """
    Создает файл конфигурации для alembic.
    """
    cfg = Config(
        file_='alembic.ini',
    )
    cfg.set_main_option('sqlalchemy.url', settings.get_db_url())
    cfg.set_main_option('script_location', 'migrator')
    return cfg
    cmd_options = SimpleNamespace(
        config="app/db/",
        name="alembic",
        pg_url=postgres,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine():
    """
    Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    return create_async_engine(settings.get_db_url(), echo=True)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    """
    Проводит миграции.
    """
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def client(migrated_postgres, manager: SessionManager = SessionManager()) -> AsyncClient:
    """
    Returns a client that can be used to interact with the application.
    """
    # app.dependency_overrides[get_current_user] = get_current_user
    manager.refresh()  # без вызова метода изменения конфига внутри фикстуры postgres не подтягиваются в класс
    yield AsyncClient(app=app, base_url="http://test")


@pytest.fixture
async def engine_async(migrated_postgres, postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session
