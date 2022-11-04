import abc
import operator as op
from typing import TYPE_CHECKING, Any, Callable, Optional

from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import Select

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
    """Filter filed by value and lookup_expr."""

    def __init__(
        self,
        field: QueryableAttribute,
        *,
        lookup_expr: Callable[[Any, Any], Any] = op.eq,
    ) -> None:
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
