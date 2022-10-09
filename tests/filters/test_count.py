from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filterset import FilterSet
from tests.filters.conftest import ItemFactory, ItemForFilters


class FilterSetClass(FilterSet):
    id = Filter(ItemForFilters, "id")


async def test_count(db_session: AsyncSession) -> None:
    three_items: list[ItemForFilters] = await ItemFactory.create_batch(3)
    filter_set = FilterSetClass({}, db_session, select(ItemForFilters))
    assert await filter_set.count() == len(three_items)


async def test_count_with_filter(db_session: AsyncSession) -> None:
    three_items: list[ItemForFilters] = await ItemFactory.create_batch(3)
    filter_set = FilterSetClass({"id": three_items[0].id}, db_session, select(ItemForFilters))
    assert await filter_set.count() == len(three_items[:1])


async def test_count_with_distinct(db_session: AsyncSession) -> None:
    three_items: list[ItemForFilters] = await ItemFactory.create_batch(3)
    filter_set = FilterSetClass({}, db_session, select(ItemForFilters))
    assert await filter_set.count(distinct=True) == len(three_items)
