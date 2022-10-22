import abc
from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional, Sequence, Tuple

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
                    date=OrderingField(Item.title, nulls=NullsPosition.last)
                    date=OrderingField(Item.id)
                )
        """
        super().__init__()
        self.fields: Dict[str, OrderingField] = fields

    def filter(self, query: Select, value: List[str]) -> Select:
        """Apply ordering to a query instance.

        :param query:
            query instance for ordering
        :param value:
            A list of strings, where each one specify
            which ordering field from available self.fields should be applied
            Also specify ordering direction
            Example::
                value = ["area", "-date", "id"]
        :returns:
            query instance after the provided ordering has been applied.
        """

        if not value:
            return query

        ordering_fields = self._get_sqlalchemy_fields(value)
        if ordering_fields:
            query = query.order_by(*ordering_fields)
        return query

    def _get_sqlalchemy_fields(self, params: List[str]) -> List[ColumnElement]:
        sqlalchemy_fields = []
        for param in params:
            reverse, param = self._parse_param(param)

            if param in EMPTY_VALUES or param not in self.fields:
                continue

            ordering: OrderingField = self.fields[param]
            sqlalchemy_fields.append(ordering.build_sqlalchemy_field(reverse))
        return sqlalchemy_fields

    @staticmethod
    def _parse_param(param: str) -> Tuple[bool, str]:
        """Parse direction and ordering field name"""
        return param.startswith("-"), param.lstrip("-")
