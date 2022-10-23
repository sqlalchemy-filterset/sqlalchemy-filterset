import abc
import operator as op
from typing import TYPE_CHECKING, Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import ColumnElement, Select

from sqlalchemy_filterset.constants import EMPTY_VALUES, NullsPosition

if TYPE_CHECKING:
    from sqlalchemy_filterset.filtersets import BaseFilterSet


class BaseFilter:
    field_name: Optional[str] = None
    "Name of Filter in FilterSet. Set by FilterSet after creation."

    def __init__(self) -> None:
        self.parent: Optional["BaseFilterSet"] = None

    @abc.abstractmethod
    def filter(self, query: Select, value: Any) -> Select:
        """Implementation of query build for this Filter"""
        ...


class Filter(BaseFilter):
    """Base Filter by filed"""

    def __init__(
        self,
        field: QueryableAttribute,
        *,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param field: Filed of Model for filtration
        :param exclude: Use inverted filtration
        :param nullable: Allow empty values in filtration process
        """
        super().__init__()
        self.field = field
        self.exclude = exclude
        self.nullable = nullable

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = self.field == value
        return query.where(~expression if self.exclude else expression)


class InFilter(Filter):
    def filter(self, query: Select, value: Sequence) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = self.field.in_(value)
        return query.where(~expression if self.exclude else expression)


# handle case when exclude
class RangeFilter(Filter):
    def __init__(
        self,
        field: QueryableAttribute,
        *,
        exclude: bool = False,
        left_operator: Callable = op.ge,
        right_operator: Callable = op.le,
    ) -> None:
        """
        :param field: Filed of Model for filtration
        :param exclude: Use inverted filtration
        :param left_operator: Comparsion operator for left_value. Available values (">=", ">")
        :param right_operator: Comparsion operator for right_value. Available values ("<=", "<")
        """

        assert left_operator in (op.ge, op.gt)
        assert right_operator in (op.le, op.lt)

        exclude_map: Dict[Callable, Callable] = {
            op.ge: op.lt,
            op.gt: op.le,
            op.le: op.gt,
            op.lt: op.ge,
        }
        self.left_operator = left_operator if not exclude else exclude_map[left_operator]
        self.right_operator = right_operator if not exclude else exclude_map[right_operator]
        self.logical_operator = sa.and_ if not exclude else sa.or_
        super().__init__(field=field, exclude=exclude)

    def filter(self, query: Select, value: Optional[Tuple[Any, Any]]) -> Select:
        """Apply filtering by range to a query instance.

        :param query: query instance for filtering
        :param value:
            A sequence of two values: left_value, right_value, where:
                left_operator - left border for range
                right_operator - right border for range
            Example::
                value = [100, 1000] - filter 100 <= value <= 1000
                value = [100, None] - filter value >= 100
                value = [None, 1000] - filter value <= 1000
                value = [datetime.now() - timedelta(days=10), datetime.now()] - filter last 10 days
        :returns: query instance after the provided filtering has been applied.
        """

        if not value:
            return query

        left_value, right_value = value
        expressions = []
        if left_value is not None:
            expressions.append(self.left_operator(self.field, left_value))
        if right_value is not None:
            expressions.append(self.right_operator(self.field, right_value))
        return query.where(self.logical_operator(*expressions))


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

    def filter(self, query: Select, value: Sequence[str]) -> Select:
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
