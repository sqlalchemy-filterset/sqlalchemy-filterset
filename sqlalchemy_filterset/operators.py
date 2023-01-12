from sqlalchemy.sql import ColumnElement

from sqlalchemy_filterset.types import ModelAttribute


def icontains(field: ModelAttribute, value: str) -> ColumnElement:
    return field.ilike(f"%{value}%")
