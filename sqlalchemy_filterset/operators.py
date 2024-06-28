from typing import Any

from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql import operators as sa_op

from sqlalchemy_filterset.types import ModelAttribute


def icontains(field: ModelAttribute, value: str) -> ColumnElement:
    return field.ilike(f"%{value}%")


def is_null(field: ModelAttribute, value: bool) -> Any:
    if not isinstance(value, bool):
        raise ValueError(
            f"Value can only be True or False, but {value} ({type(value)}) was provided"
        )
    sa_ops = {
        True: sa_op.is_,
        False: sa_op.is_not,
    }
    return sa_ops[value](field, b=None)
