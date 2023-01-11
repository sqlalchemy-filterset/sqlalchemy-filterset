import abc
import inspect
import operator as op
from typing import TYPE_CHECKING, Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import ColumnElement, Select
from sqlalchemy.sql import operators as sa_op

from sqlalchemy_filterset.constants import NullsPosition
from sqlalchemy_filterset.operators import icontains
from sqlalchemy_filterset.strategies import BaseStrategy
from sqlalchemy_filterset.types import LookupExpr

if TYPE_CHECKING:
    from sqlalchemy_filterset.filtersets import BaseFilterSet  # pragma: no cover


class BaseFilter:
    """A Base class for all filters.

    Attributes
        field_name: Name of Filter in FilterSet. Set by FilterSet after creation.
    """

    field_name: Optional[str] = None

    def __init__(self) -> None:
        self._filter_set: Optional["BaseFilterSet"] = None

    @property
    def filter_set(self) -> Optional["BaseFilterSet"]:
        """FilterSet of this Filter"""
        return self._filter_set  # pragma: no cover

    @filter_set.setter
    def filter_set(self, value: "BaseFilterSet") -> None:
        self._filter_set = value

    @abc.abstractmethod
    def filter(self, query: Select, value: Any, values: Dict[str, Any]) -> Select:
        """Implementation of query build for this Filter"""
        ...  # pragma: no cover


class Filter(BaseFilter):
    """Filter results by field, value and lookup_expr."""

    def __init__(
        self,
        field: QueryableAttribute,
        *,
        lookup_expr: LookupExpr = op.eq,
        strategy: Optional[BaseStrategy] = None,
    ) -> None:
        """
        :param field: Model filed for filtration
        :param lookup_expr: Comparison operator from modules:
         operator, sqlalchemy.sql.operators or custom operator
        """
        super().__init__()

        self.field = field
        self.lookup_expr = lookup_expr
        self.strategy = strategy if strategy is not None else BaseStrategy()

    def filter(self, query: Select, value: Any, values: Dict[str, Any]) -> Select:
        """Apply filtering by lookup_expr to a query instance."""
        return self.strategy.filter(query, self.lookup_expr(self.field, value))


class InFilter(Filter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs, lookup_expr=sa_op.in_op)


class NotInFilter(Filter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs, lookup_expr=sa_op.not_in_op)


class BooleanFilter(Filter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs, lookup_expr=sa_op.is_)


class RangeFilter(BaseFilter):
    """Filter results by field within specified range."""

    def __init__(
        self,
        field: QueryableAttribute,
        *,
        left_lookup_expr: LookupExpr = op.ge,
        right_lookup_expr: LookupExpr = op.le,
        logic_expr: Callable = sa.and_,
        strategy: Optional[BaseStrategy] = None,
    ) -> None:
        """
        :param field: Filed of Model for filtration
        :param left_lookup_expr: Comparsion operator for the left border of the range.
            default callable for comparison op: op.ge, op.gt, op.le, op.lt
        :param right_lookup_expr: Comparsion operator for the right border of the range.
            default callable for comparison op: op.ge, op.gt, op.le, op.lt
        :param logic_expr: and/or operator to produce a conjunction of border expressions
        """
        super().__init__()

        self.field = field
        self.left_lookup_expr = left_lookup_expr
        self.right_lookup_expr = right_lookup_expr
        self.logic_expr = logic_expr
        self.strategy = strategy if strategy is not None else BaseStrategy()

    def filter(
        self, query: Select, value: Optional[Tuple[Any, Any]], values: Dict[str, Any]
    ) -> Select:
        """Apply filtering by range to a query instance.

        :param query: query instance for filtering
        :param value: A tuple with two values to filter left and right border of the range

        :returns: query instance after the provided filtering has been applied.
        """

        if not value:
            return query

        left_value, right_value = value
        expressions = []
        if left_value is not None:
            expressions.append(self.left_lookup_expr(self.field, left_value))
        if right_value is not None:
            expressions.append(self.right_lookup_expr(self.field, right_value))
        return self.strategy.filter(query, self.logic_expr(*expressions))


class OrderingField(NamedTuple):
    field: QueryableAttribute
    nulls: Optional[NullsPosition] = None

    def build_sqlalchemy_field(self, reverse: bool) -> ColumnElement:
        """Build sqlalchemy ordering field
        based on predefined parameters and passed ordering direction"""
        field = self.field.asc() if not reverse else self.field.desc()

        if self.nulls == NullsPosition.first:
            field = field.nullsfirst()
        elif self.nulls == NullsPosition.last:
            field = field.nullslast()
        return field


class OrderingFilter(BaseFilter):
    def __init__(self, **fields: OrderingField) -> None:
        """
        :param fields: Fields available for future ordering

        Example::

            ordering_filter = OrderingFilter(
                area=OrderingField(Item.area),
                title=OrderingField(Item.title, nulls=NullsPosition.last),
                id=OrderingField(Item.id)
            )
        """
        super().__init__()
        self.fields: Dict[str, OrderingField] = fields

    def filter(self, query: Select, value: Sequence[str], values: Dict[str, Any]) -> Select:
        """Apply ordering to a query instance.

        :param query: query instance for ordering
        :param value:
            A sequence of strings, where each one specify
            which ordering field from available self.fields should be applied
            Also specify ordering direction

        :returns: query instance after the provided ordering has been applied.

        Example::

            OrderingFilter(select(Item), value=["area", "-date", "id"])
        """

        if not value:
            return query

        ordering_fields = self._get_sqlalchemy_fields(value)
        if ordering_fields:
            query = query.order_by(*ordering_fields)
        return query

    def _get_sqlalchemy_fields(self, params: Sequence[str]) -> List[ColumnElement]:
        sqlalchemy_fields = []
        for param in params:
            reverse, param = self._parse_param(param)

            if not param or param not in self.fields:
                continue
            ordering: OrderingField = self.fields[param]
            sqlalchemy_fields.append(ordering.build_sqlalchemy_field(reverse))
        return sqlalchemy_fields

    @staticmethod
    def _parse_param(param: str) -> Tuple[bool, str]:
        """Parse direction and ordering field name"""
        return param.startswith("-"), param.lstrip("-")


class LimitOffsetFilter(BaseFilter):
    """Filter for managing limit and offset"""

    def filter(
        self,
        query: Select,
        value: Optional[Tuple[Optional[int], Optional[int]]],
        values: Dict[str, Any],
    ) -> Select:
        """Apply limit offset pagination to a query instance.

        :param query: query instance for pagination
        :param value: A tuple of positive integers (limit, offset)
        :returns: query instance after the provided pagination has been applied.

        Example::

            LimitOffsetFilter(select(Item), value=(100, 0))
        """

        if not value:
            return query

        limit, offset = value
        return query.limit(limit).offset(offset)


class MethodFilter(BaseFilter):
    """This helper is used to override Filter.filter() when a 'method' argument
    is passed. It proxies the call to the actual method on the filter's parent filterset.
    """

    def __init__(self, method: str) -> None:
        """
        :param method: Method name in parent FilterSet
        """
        super().__init__()
        self.method = method
        self._filter: Optional[Callable] = None

    @property
    def filter_set(self) -> Optional["BaseFilterSet"]:
        """FilterSet of this Filter"""
        return self._filter_set

    @filter_set.setter
    def filter_set(self, value: "BaseFilterSet") -> None:
        self._filter_set = value
        self.init_filter_method()

    def init_filter_method(self) -> None:
        from sqlalchemy_filterset.filtersets import BaseFilterSet

        assert isinstance(self.filter_set, BaseFilterSet)
        assert hasattr(self.filter_set, self.method)
        self._filter = getattr(self.filter_set, self.method)

    def filter(self, query: Select, value: Any, values: Dict[str, Any]) -> Select:
        assert self._filter
        params = {"query": query, "value": value, "values": values}
        attrs = inspect.getfullargspec(self._filter).args
        required_attrs = {k: v for k, v in params.items() if k in attrs}
        return self._filter(**required_attrs)


class SearchFilter(BaseFilter):
    """Filter for searching by a given search string"""

    def __init__(
        self,
        *fields: Sequence[QueryableAttribute],
        lookup_expr: LookupExpr = icontains,
        logic_expr: Callable = sa.or_,
    ) -> None:
        """
        :param fields: Fields for search
        :param search_type: Type of search
        :param search_expr: and/or operator to produce a conjunction of search expressions
        """
        super().__init__()
        self.fields = fields
        self.lookup_expr = lookup_expr
        self.logic_expr = logic_expr

    def filter(self, query: Select, value: Optional[str], values: Dict[str, Any]) -> Select:
        """Apply search to a query instance.

        :param query: query instance for search
        :param value: A string to search
        :returns: query instance after the provided search has been applied.
        """

        if not value:
            return query

        expressions = []
        for field in self.fields:
            expressions.append(self.lookup_expr(field, value))
        return query.where(self.logic_expr(*expressions))
