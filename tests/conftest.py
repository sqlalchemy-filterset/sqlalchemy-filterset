import asyncio
import sys
from asyncio import AbstractEventLoop
from typing import Any, AsyncIterator, Dict, Generator, Iterator, Optional

import pytest
from pydantic import BaseSettings, PostgresDsn, validator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from tests.async_alchemy_factory import AsyncSQLAlchemyModelFactory
from tests.database import Base


class PostgresConfig(BaseSettings):
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: str = "5432"
    user: str = "postgres"
    password: str = "postgres"
    db: str = "postgres"
    dsn: Optional[PostgresDsn] = None

    @validator("dsn", pre=True)
    def assemble_dsn(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.get("scheme"),
            user=values.get("user"),
            password=values.get("password"),
            host=values.get("host"),
            port=values.get("port"),
            path=f"/{values.get('db')}",
        )

    class Config:
        env_prefix = "postgres_"
        env_file = ".env"


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    """
    Creates an instance of the default event loop for the test session.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def async_database_url(worker_id: str) -> str:
    return f"{PostgresConfig(scheme='postgresql+asyncpg').dsn}-{worker_id}"


@pytest.fixture(scope="session")
def sync_database_url(worker_id: str) -> str:
    return f"{PostgresConfig(scheme='postgresql').dsn}-{worker_id}"


@pytest.fixture(scope="session", autouse=True)
def database(sync_database_url: str) -> Iterator[None]:
    if database_exists(sync_database_url):
        drop_database(sync_database_url)
    create_database(sync_database_url)
    engine = create_engine(sync_database_url)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    drop_database(sync_database_url)


@pytest.fixture()
def sync_session(sync_database_url: str) -> Iterator[Session]:
    engine = create_engine(sync_database_url)
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()

    try:
        yield session
    finally:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        session.commit()
        session.close()


@pytest.fixture()
async def async_session(async_database_url: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(async_database_url)

    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    session: AsyncSession = Session()

    try:
        yield session
    finally:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
        await session.close()


@pytest.fixture(autouse=True)
def init_factories(async_session: AsyncSession) -> None:
    """Init factories."""
    AsyncSQLAlchemyModelFactory._session = async_session
