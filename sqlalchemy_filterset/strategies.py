import abc
from abc import ABC
from typing import Any, Optional

from sqlalchemy import inspect, select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import Select


class BaseStrategy:
    def __init__(
        self, field: QueryableAttribute, target_fk: Optional[QueryableAttribute] = None
    ) -> None:
        self.field = field
        self.target_fk = target_fk

    def filter(self, query: Select, expression: Any) -> Select:
        return query.where(expression)


class RelationBaseJoinedStrategy(ABC, BaseStrategy):
    def filter(self, query: Select, expression: Any) -> Select:

        query = self._join_if_necessary(query)
        return query.where(expression)

    def _join_if_necessary(self, query: Select) -> Select:
        onclouse = None

        if self.target_fk:
            # todo: ins.primary_key не всегда верный вариант
            onclouse = self.target_fk == inspect(self.field.class_).primary_key

        joined_before = False
        for join in query._setup_joins:  # type: ignore
            if join[0] == self.field.class_.__table__:
                joined_before = True
                break

        if not joined_before:
            query = self._build_join(query, onclouse=onclouse)
        return query

    @abc.abstractmethod
    def _build_join(self, query: Select, **kwargs: Any) -> Select:
        ...


class RelationInnerJoinedStrategy(RelationBaseJoinedStrategy):
    def _build_join(self, query: Select, **kwargs: Any) -> Select:
        return query.join(self.field.class_, **kwargs)


class RelationOuterJoinedStrategy(RelationBaseJoinedStrategy):
    def _build_join(self, query: Select, **kwargs: Any) -> Select:
        return query.outerjoin(self.field.class_, **kwargs)


class RelationSubqueryExistsStrategy(BaseStrategy):
    def __init__(self, field: QueryableAttribute, target_fk: QueryableAttribute) -> None:
        assert target_fk is not None, "target_fk is required for RelationSubqueryExistsStrategy"
        super().__init__(field, target_fk)

    def filter(self, query: Select, expression: Any) -> Select:
        ins = inspect(self.field.class_)
        subquery = (
            select(self.field.class_)
            .where(ins.primary_key == self.target_fk)
            .where(expression)
            .exists()
        )
        return query.where(subquery)
