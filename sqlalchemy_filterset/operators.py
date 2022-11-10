from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import ColumnElement


def ilike_contains(field: QueryableAttribute, value: str) -> ColumnElement:
    return field.ilike(f"%{value}%")
