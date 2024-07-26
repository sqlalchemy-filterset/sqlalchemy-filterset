import copy
from typing import Any, List, Type, Union

from sqlalchemy import literal_column, select
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.selectable import Exists, Join, ScalarSelect

from sqlalchemy_filterset.types import Model


class BaseStrategy:
    def filter(self, query: Select, expression: Any) -> Select:
        return query.where(expression)


class RelationJoinStrategy(BaseStrategy):
    def __init__(self, model: Type[Model], onclause: ColumnElement[bool]) -> None:
        self.model = model
        self.onclause = onclause
        self.is_outer = False
        self.is_full = False

    def filter(self, query: Select, expression: Any) -> Select:
        query = self.apply_join(query)
        return query.where(expression)

    def apply_join(self, query: Select) -> Select:
        return self._join_if_necessary(query)

    def _join_if_necessary(self, query: Select) -> Select:
        joined_before = False
        to_check = list(query.get_final_froms())
        while to_check:
            element = to_check.pop()
            if not isinstance(element, Join):
                continue

            if (
                element.right == self.model.__table__
                and element.onclause is not None
                and element.onclause.compare(self.onclause)
                and element.isouter == self.is_outer
                and element.full == self.is_full
            ):
                joined_before = True
                break

            to_check.append(element.left)
            to_check.append(element.right)

        if not joined_before:
            query = self._build_join(query, onclause=self.onclause)
        return query

    def _build_join(self, query: Select, onclause: ColumnElement[bool]) -> Select:
        return query.join(self.model, onclause=onclause)


class RelationOuterJoinStrategy(RelationJoinStrategy):
    def _build_join(self, query: Select, onclause: ColumnElement[bool]) -> Select:
        return query.outerjoin(self.model, onclause=onclause)


class JoinChainStrategy(BaseStrategy):
    def __init__(
        self,
        *chain: RelationJoinStrategy,
    ) -> None:
        self.chain = chain

    def filter(self, query: Select, expression: Any) -> Select:
        for el in self.chain:
            query = el.apply_join(query)
        return query.where(expression)


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
