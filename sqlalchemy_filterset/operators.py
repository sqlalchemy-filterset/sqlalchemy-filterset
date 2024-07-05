from typing import Any

from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql import operators as sa_op

from sqlalchemy_filterset.types import ModelAttribute


def icontains(field: ModelAttribute, value: str) -> ColumnElement:
    return field.ilike(f"%{value}%")


def is_null(field: ModelAttribute, value: bool) -> Any:
    if value:
        return sa_op.is_(field, None)
    else:
        return sa_op.is_not(field, None)
