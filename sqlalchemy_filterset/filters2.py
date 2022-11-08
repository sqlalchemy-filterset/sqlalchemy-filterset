import abc
import operator as op
from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import Select

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
        self.parent: Optional["BaseFilterSet"] = None

    @abc.abstractmethod
    def filter(self, query: Select, value: Any) -> Select:
        """Implementation of query build for this Filter"""
        ...  # pragma: no cover


class Filter(BaseFilter):
    """Filter results by field, value and lookup_expr."""

    def __init__(self, field: QueryableAttribute, *, lookup_expr: LookupExpr = op.eq) -> None:
        """
        :param field: Model filed for filtration
        :param lookup_expr: Comparison operator from modules:
         operator, sqlalchemy.sql.operators or custom operator
        """
        super().__init__()

        self.field = field
        self.lookup_expr = lookup_expr

    def filter(self, query: Select, value: Any) -> Select:
        """Apply filtering by lookup_expr to a query instance."""

        return query.where(self.lookup_expr(self.field, value))


class RangeFilter(BaseFilter):
    """Filter results by field within specified range."""

    def __init__(
        self,
        field: QueryableAttribute,
        *,
        left_lookup_expr: LookupExpr = op.ge,
        right_lookup_expr: LookupExpr = op.le,
        logic_expr: Callable = sa.and_,
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

    def filter(self, query: Select, value: Optional[Tuple[Any, Any]]) -> Select:
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
        return query.where(self.logic_expr(*expressions))
