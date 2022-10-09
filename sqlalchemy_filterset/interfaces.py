import abc
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from sqlalchemy_filterset.filters import BaseFilter


class IBaseFilter(abc.ABC):
    """Абстрактный класс фильтра"""

    def __init__(self) -> None:
        self._parent: Optional["IFilterSet"] = None

    @property
    def parent(self) -> Optional["IFilterSet"]:
        """FilterSet родитель, данного фильтра"""
        return self._parent

    @parent.setter
    def parent(self, value: "IFilterSet") -> None:
        self._parent = value


class IFilterSet(abc.ABC):
    declared_filters: Dict[str, "BaseFilter"]

    @abc.abstractmethod
    async def filter(self) -> Any:
        ...

    @abc.abstractmethod
    async def count(self) -> int:
        ...
