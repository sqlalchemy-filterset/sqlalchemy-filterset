from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filterset import FilterSet
from sqlalchemy_filterset.constants import EMPTY_VALUES
from tests.filters.conftest import ItemFactory
from tests.models import ItemForFilters, Parent, GrandParent, GrandGrandParent


class FilterSetClass(FilterSet):
    id = Filter(ItemForFilters, "id")
    ids = InFilter(ItemForFilters, "id")


@pytest.mark.parametrize("empty_value", EMPTY_VALUES)
@pytest.mark.parametrize("field", ["id", "ids"])
async def test_empty_values(empty_value: Any, field: str, db_session: AsyncSession) -> None:
    three_items: list[ItemForFilters] = await ItemFactory.create_batch(3)
    base_query = select(ItemForFilters).join(Parent).join(GrandParent).join(GrandGrandParent)
    f = FilterSetClass({f"{field}": empty_value}, db_session, base_query)
    result = await db_session.execute(f.filter_query())
    actual = result.scalars().all()
    #objects_equals(actual, three_items)


async def test_wrong_field(db_session: AsyncSession) -> None:
    three_items: list[ItemForFilters] = await ItemFactory.create_batch(3)
    base_query = select(ItemForFilters).join(Parent).join(GrandParent).join(GrandGrandParent)
    f = FilterSetClass({"test": "test"}, db_session, base_query)
    result = await db_session.execute(f.filter_query())
    actual = result.scalars().all()
    #objects_equals(actual, three_items)
