from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import ColumnElement


def icontains(field: QueryableAttribute, value: str) -> ColumnElement:
    return field.ilike(f"%{value}%")
