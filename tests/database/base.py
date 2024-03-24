import re
from typing import Any, Union
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.declarative import as_declarative, declared_attr


def camel_to_snake(came_str: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", came_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


@as_declarative()
class Base:
    id: Union[sa.Column[int], sa.Column[UUID]]
    metadata: sa.MetaData

    __table__: sa.Table

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # Для корректной работы mypy
        pass

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa
        return camel_to_snake(cls.__name__)  # type: ignore

    __mapper_args__ = {"eager_defaults": True}
    __allow_unmapped__ = True
