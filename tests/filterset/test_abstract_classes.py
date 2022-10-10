import abc
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filterset import FilterSet
from tests.models import ItemForFilters


class AbstractFilterSetClass(FilterSet):
    id = Filter(ItemForFilters, "id")
    ids = InFilter(ItemForFilters, "id")

    @abc.abstractmethod
    async def some_method(self) -> Any:
        ...


async def test_abstract_filter_set(db_session: AsyncSession) -> None:
    base_query = select(ItemForFilters)
    with pytest.raises(TypeError):
        AbstractFilterSetClass({"test": "test"}, db_session, base_query)  # type: ignore
