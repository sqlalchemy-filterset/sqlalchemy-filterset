import asyncio
import sys
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Callable, Generator, Sequence

import pytest
from pytest_async_sqlalchemy import create_database, drop_database
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncTransaction
from sqlalchemy.orm import sessionmaker

from tests.async_alchemy_factory import AsyncSQLAlchemyModelFactory
from tests.database import Base
from tests.database.base import WrappedAsyncSession


class PostgresConfig:
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: str = "15432"
    user: str = "postgres"
    password: str = "postgres"
    db: str = "test"
    pool_size: int = 10
    pool_overflow_size: int = 10
    leader_usage_coefficient: float = 0.3
    echo: bool = False
    autoflush: bool = False
    autocommit: bool = False
    expire_on_commit: bool = False
    engine_health_check_delay: int = 1
    slave_hosts: Sequence[str] | str = ""
    slave_dsns: Sequence[str] | str = ""

    @property
    def dsn(self) -> str:
        return "{scheme}://{user}:{password}@{host}:{port}/{db}".format(
            scheme=self.scheme,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            db=self.db,
        )


db_config = PostgresConfig()
logger.warning(db_config.dsn)


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
