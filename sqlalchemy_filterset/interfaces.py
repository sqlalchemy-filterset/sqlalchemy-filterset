import abc
from collections import OrderedDict
from typing import Any, Callable, Optional

from sqlalchemy.orm import Bundle
from sqlalchemy.sql import ColumnElement


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
    declared_filters: OrderedDict

    @abc.abstractmethod
    async def filter(self) -> Any:
        ...

    @abc.abstractmethod
    async def count(self) -> int:
        ...
