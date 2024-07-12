import copy
from abc import ABC, abstractmethod
from typing import Any, List, Type, Union

from sqlalchemy import literal_column, select
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.selectable import Exists, ScalarSelect

from sqlalchemy_filterset.types import Model


class BaseStrategy:
    def filter(self, query: Select, expression: Any) -> Select:
        return query.where(expression)

    def __eq__(self, another_strategy) -> bool:
        return False


class ApplicableStrategy(BaseStrategy, ABC):
    @abstractmethod
    def apply(self, query: Select) -> Select:
        ...


class RelationJoinStrategy(ApplicableStrategy):
    def __init__(self, model: Type[Model], onclause: ColumnElement[bool]) -> None:
        self.model = model
        self.onclause = onclause

    def apply(self, query: Select) -> Select:
        return self._build_join(query, self.onclause)

    def _build_join(self, query: Select, onclause: ColumnElement[bool]) -> Select:
        return query.join(self.model, onclause=onclause)

    def __eq__(self, another_strategy) -> bool:
        return (
            isinstance(another_strategy, RelationJoinStrategy)
            and type(self) == type(another_strategy)
            and self.model == another_strategy.model
            and self.onclause.compare(another_strategy.onclause)
        )


class RelationOuterJoinStrategy(RelationJoinStrategy):
    def _build_join(self, query: Select, onclause: ColumnElement[bool]) -> Select:
        return query.outerjoin(self.model, onclause=onclause)


class RelationSubqueryExistsStrategy(BaseStrategy):
    """
    This strategy makes exist subquery to a related model.
    It also contains optimization:
    if the query already has a similar subquery (has equal target table and onclause expression) -
    it reuses similar subquery by adding new where expressions.
    """

    def __init__(self, model: Type[Model], onclause: ColumnElement[bool]) -> None:
        self.model = model
        self.onclause = onclause

    def filter(self, query: Select, expression: Any) -> Select:
        existed_subquery_index = self._get_where_criteria_index_of_subquery_with_same_onclause(
            query
        )
        if existed_subquery_index is None:
            return query.where(
                select(literal_column("1"))
                .select_from(self.model)
                .where(self.onclause, expression)
                .exists()
            )

        # Create new query and change where criteria to new subquery with expression
        query = copy.copy(query)
        new_where_criteria: List = list(query._where_criteria)
        new_where_criteria[existed_subquery_index] = new_where_criteria[
            existed_subquery_index
        ].where(expression)
        query._where_criteria = tuple(new_where_criteria)
        return query

    def _get_where_criteria_index_of_subquery_with_same_onclause(
        self, query: Select
    ) -> Union[int, None]:
        """
        Get index of _where_criteria element which is the same subquery as we need for filtering
        """
        where_criteria = query._where_criteria
        for index, clause in enumerate(where_criteria):
            if (
                isinstance(clause, Exists)
                and isinstance(clause.element, ScalarSelect)
                and isinstance(clause.element.element, Select)
            ):
                base_query_of_exists = clause.element.element
                # Check base_query_of_exists is selecting from target table
                if self.model.__table__ not in base_query_of_exists.froms:
                    continue
                if self.__is_query_contains_onclause(base_query_of_exists, self.onclause):
                    return index
        return None

    @staticmethod
    def __is_query_contains_onclause(query: Select, onclause: ColumnElement[bool]) -> bool:
        for onclouse in query.whereclause.clauses:  # type: ignore
            if onclause.compare(onclouse):
                return True
        return False
