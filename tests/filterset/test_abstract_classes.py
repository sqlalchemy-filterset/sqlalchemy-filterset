import abc
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.sql import operators as sa_op

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models import Item


class AbstractFilterSetClass(BaseFilterSet):
    id = Filter(Item.id)
    ids = Filter(Item.id, lookup_expr=sa_op.in_op)

    @abc.abstractmethod
    async def some_method(self) -> Any:
        ...


def test_abstract_filter_set() -> None:
    with pytest.raises(TypeError):
        AbstractFilterSetClass({"test": "test"}, select(Item.id))  # type: ignore
