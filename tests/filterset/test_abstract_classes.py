import abc
from typing import Any

import pytest
from sqlalchemy import select

from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models.base import Item


class AbstractFilterSetClass(BaseFilterSet):
    id = Filter(Item.id)
    ids = InFilter(Item.id)

    @abc.abstractmethod
    async def some_method(self) -> Any:
        ...  # pragma: no cover


def test_abstract_filter_set() -> None:
    with pytest.raises(TypeError):
        AbstractFilterSetClass({"test": "test"}, select(Item.id))  # type: ignore
