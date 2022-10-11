import typing

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filtersets import AsyncFilterSet
from tests.filterset.conftest import ItemFactory, ItemForFilters


class ItemFilterSet(AsyncFilterSet):
    id = Filter(ItemForFilters, "id")


async def test_count(db_session: AsyncSession) -> None:
    three_items: typing.List[ItemForFilters] = await ItemFactory.create_batch(3)
    filter_set = ItemFilterSet({}, db_session, select(ItemForFilters))
    assert await filter_set.count() == len(three_items)


async def test_count_with_filter(db_session: AsyncSession) -> None:
    three_items: typing.List[ItemForFilters] = await ItemFactory.create_batch(3)
    filter_set = ItemFilterSet({"id": three_items[0].id}, db_session, select(ItemForFilters))
    assert await filter_set.count() == len(three_items[:1])


async def test_count_with_distinct(db_session: AsyncSession) -> None:
    three_items: typing.List[ItemForFilters] = await ItemFactory.create_batch(3)
    filter_set = ItemFilterSet({}, db_session, select(ItemForFilters).distinct())
    assert await filter_set.count() == len(three_items)
