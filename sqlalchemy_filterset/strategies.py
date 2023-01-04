import abc
import logging
from abc import ABC
from typing import Any

from sqlalchemy import literal_column, select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import Select

logger = logging.getLogger(__name__)


class BaseStrategy:
    def __init__(self, field: QueryableAttribute, onclause: Any = None) -> None:
        self.field = field
        self.onclause = onclause

    def filter(self, query: Select, expression: Any) -> Select:
        return query.where(expression)


class RelationBaseJoinStrategy(ABC, BaseStrategy):
    def filter(self, query: Select, expression: Any) -> Select:
        query = self._join_if_necessary(query)
        return query.where(expression)

    def _join_if_necessary(self, query: Select) -> Select:
        joined_before = False
        for join in query.froms:
            if hasattr(join, "right") and hasattr(join, "onclause"):
                if join.right == self.field.class_.__table__:
                    if self.onclause is None:
                        # todo: make onclause required?
                        logger.warning(
                            "Can't compare onclause of joins, "
                            "double join preventing doesn't work"
                        )
                        continue
                    if join.onclause.compare(self.onclause):
                        joined_before = True
                        break

        if not joined_before:
            query = self._build_join(query, onclause=self.onclause)
        return query

    @abc.abstractmethod
    def _build_join(self, query: Select, onclause: Any) -> Select:
        ...  # pragma: no cover


class RelationInnerJoinStrategy(RelationBaseJoinStrategy):
    def _build_join(self, query: Select, onclause: Any) -> Select:
        return query.join(self.field.class_, onclause=onclause)


class RelationOuterJoinStrategy(RelationBaseJoinStrategy):
    def _build_join(self, query: Select, onclause: Any) -> Select:
        return query.outerjoin(self.field.class_, onclause=onclause)


class RelationSubqueryExistsStrategy(BaseStrategy):
    def __init__(self, field: QueryableAttribute, onclause: Any) -> None:
        assert onclause is not None, f"onclause is required for {self.__class__.__name__}"
        super().__init__(field, onclause)

    def filter(self, query: Select, expression: Any) -> Select:
        from sqlalchemy.sql.elements import BooleanClauseList
        from sqlalchemy.sql.selectable import Exists, SelectStatementGrouping

        new_where_criteria = list(query._where_criteria)
        table_match = False
        clause_match = False
        for i in range(len(new_where_criteria)):
            clause = new_where_criteria[i]
            if (
                isinstance(clause, Exists)
                and isinstance(clause.element, SelectStatementGrouping)
                and isinstance(clause.element.element, Select)
            ):
                table_match = False
                clause_match = False
                for from_table in clause.element.element._from_obj:  # type: ignore
                    if from_table == self.field.class_.__table__:
                        table_match = True
                        break
                if isinstance(clause.element.element.whereclause, BooleanClauseList):
                    for onclouse in clause.element.element.whereclause.clauses:
                        if self.onclause.compare(onclouse):
                            clause_match = True
                            break

                if clause_match and table_match:
                    new_where_criteria[i] = clause.where(expression)
                    break

        query._where_criteria = tuple(new_where_criteria)
        if clause_match and table_match:
            return query
        else:
            return query.where(
                select(literal_column("1"))
                .select_from(self.field.class_)
                .where(self.onclause, expression)
                .exists()
            )
