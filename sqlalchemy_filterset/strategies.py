import abc
from abc import ABC
from typing import Any

from sqlalchemy import literal_column, select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import Select


class BaseStrategy:
    def __init__(self, field: QueryableAttribute, onclause: Any = None) -> None:
        self.field = field
        self.onclause = onclause

    def filter(self, query: Select, expression: Any) -> Select:
        return query.where(expression)


class RelationBaseJoinedStrategy(ABC, BaseStrategy):
    def filter(self, query: Select, expression: Any) -> Select:
        query = self._join_if_necessary(query)
        return query.where(expression)

    def _join_if_necessary(self, query: Select) -> Select:
        joined_before = False
        for join in query._setup_joins:  # type: ignore
            if join[0] == self.field.class_.__table__:
                joined_before = True
                break

        if not joined_before:
            query = self._build_join(query, onclause=self.onclause)
        return query

    @abc.abstractmethod
    def _build_join(self, query: Select, onclause: Any) -> Select:
        ...  # pragma: no cover


class RelationInnerJoinedStrategy(RelationBaseJoinedStrategy):
    def _build_join(self, query: Select, onclause: Any) -> Select:
        return query.join(self.field.class_, onclause=onclause)


class RelationOuterJoinedStrategy(RelationBaseJoinedStrategy):
    def _build_join(self, query: Select, onclause: Any) -> Select:
        return query.outerjoin(self.field.class_, onclause=onclause)


class RelationSubqueryExistsStrategy(BaseStrategy):
    def __init__(self, field: QueryableAttribute, onclause: Any) -> None:
        assert onclause is not None, f"onclause is required for {self.__class__.__name__}"
        super().__init__(field, onclause)

    def filter(self, query: Select, expression: Any) -> Select:
        return query.where(
            select(literal_column("1"))
            .select_from(self.field.class_)
            .where(self.onclause, expression)
            .exists()
        )
