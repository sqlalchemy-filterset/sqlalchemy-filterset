import re
from typing import Any, Union
from uuid import UUID

from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped


def camel_to_snake(came_str: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", came_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


@as_declarative()
class Base:
    id: Union[Mapped[int], Mapped[UUID]]
    metadata: MetaData

    __table__: Table

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # Для корректной работы mypy
        pass

    @declared_attr
    def __tablename__(cls) -> str:  # noqa
        return camel_to_snake(cls.__name__)

    __mapper_args__ = {"eager_defaults": True}
    __allow_unmapped__ = True
