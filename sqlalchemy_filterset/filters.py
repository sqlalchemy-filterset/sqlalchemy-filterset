import abc
from typing import TYPE_CHECKING, Any, Optional, Sequence

from sqlalchemy.sql import Select

from sqlalchemy_filterset.constants import EMPTY_VALUES

if TYPE_CHECKING:
    from sqlalchemy_filterset.filtersets import BaseFilterSet


class BaseFilter:
    field_name: Optional[str] = None
    "Name of Filter in FilterSet. Set by FilterSet after creation."

    def __init__(self) -> None:
        self._parent: Optional["BaseFilterSet"] = None

    @property
    def parent(self) -> Optional["BaseFilterSet"]:
        """FilterSet parent of this Filter"""
        return self._parent

    @parent.setter
    def parent(self, value: "BaseFilterSet") -> None:
        self._parent = value

    @abc.abstractmethod
    def filter(self, query: Select, value: Any) -> Select:
        """Implementation of query build for this Filter"""
        ...


class Filter(BaseFilter):
    """Base Filter by filed"""

    def __init__(
        self,
        model: Any,
        field: str,
        *,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Model for filtration
        :param field: Filed of Model for filtration
        :param exclude: Use inverted filtration
        :param nullable: Allow empty values in filtration process
        """
        super().__init__()
        self.model = model
        self.field = field
        self.exclude = exclude
        self.nullable = nullable

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field) == value
        return query.where(~expression if self.exclude else expression)


class InFilter(Filter):
    def filter(self, query: Select, value: Sequence) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field).in_(value)
        return query.where(~expression if self.exclude else expression)
