import asyncio
import sys
from asyncio import AbstractEventLoop
from typing import Any, Callable, Dict, Generator, Optional

import pytest
from pydantic import BaseSettings, PostgresDsn, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

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


db_config = PostgresConfig()


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
def _database_url() -> str:
    return f"{db_config.dsn}"


@pytest.fixture(scope="session")
def init_database() -> Callable:
    return Base.metadata.create_all


@pytest.fixture(autouse=True)
def init_factories(db_session: AsyncSession) -> None:
    """Init factories."""
    AsyncSQLAlchemyModelFactory._session = db_session


@pytest.fixture()
def sync_db_session(db_session: AsyncSession) -> Session:
    return db_session.sync_session
