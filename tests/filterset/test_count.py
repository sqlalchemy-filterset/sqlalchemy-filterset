import datetime
import typing

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filtersets import AsyncFilterSet
from tests.models.factories import Item, ItemFactory


class ItemFilterSet(AsyncFilterSet):
    id = Filter(Item.id)


async def test_count(db_session: AsyncSession) -> None:
    three_items: typing.List[Item] = await ItemFactory.create_batch(3)
    filter_set = ItemFilterSet(db_session, select(Item))
    assert await filter_set.count({}) == len(three_items)


async def test_count_with_filter(db_session: AsyncSession) -> None:
    three_items: typing.List[Item] = await ItemFactory.create_batch(3)
    filter_set = ItemFilterSet(db_session, select(Item))
    assert await filter_set.count({"id": three_items[0].id}) == len(three_items[:1])


async def test_count_with_distinct(db_session: AsyncSession) -> None:
    three_items: typing.List[Item] = await ItemFactory.create_batch(3)
    filter_set = ItemFilterSet(db_session, select(Item).distinct())
    assert await filter_set.count({}) == len(three_items)


async def test_count_with_distinct_on(db_session: AsyncSession) -> None:
    await ItemFactory(title="first", date=datetime.date(year=2000, month=10, day=2))
    await ItemFactory(title="first", date=datetime.date(year=2000, month=10, day=1))
    await ItemFactory()
    query = select(Item).distinct(Item.title).order_by(Item.title, Item.date.desc())
    filter_set = ItemFilterSet(db_session, query)
    assert await filter_set.count({}) == 2
