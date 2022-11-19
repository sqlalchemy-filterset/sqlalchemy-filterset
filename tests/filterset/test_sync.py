import typing

from sqlalchemy import select
from sqlalchemy.orm import Session

from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filtersets import FilterSet
from tests.models import Item
from tests.models.factories import ItemFactory


class ItemFilterSet(FilterSet[Item]):
    id = Filter(Item.id)
    ids = InFilter(Item.id)


class TestSyncFilterSet:
    base_query = select(Item)

    async def test_filter(self, sync_session: Session) -> None:
        three_items: typing.List[Item] = await ItemFactory.create_batch(3)
        filter_set = ItemFilterSet(sync_session, self.base_query)
        result = filter_set.filter({"id": three_items[0].id})
        assert len(result) == 1
        assert result[0].id == three_items[0].id

    async def test_filter_ids(self, sync_session: Session) -> None:
        three_items: typing.List[Item] = await ItemFactory.create_batch(3)
        filter_set = ItemFilterSet(sync_session, self.base_query)
        result = filter_set.filter({"ids": [item.id for item in three_items]})
        assert {item.id for item in three_items} == {item.id for item in result}

    async def test_count(self, sync_session: Session) -> None:
        three_items: typing.List[Item] = await ItemFactory.create_batch(3)
        filter_set = ItemFilterSet(sync_session, select(Item))
        assert filter_set.count({}) == len(three_items)

    async def test_count_ids(self, sync_session: Session) -> None:
        three_items: typing.List[Item] = await ItemFactory.create_batch(3)
        filter_set = ItemFilterSet(sync_session, select(Item))
        assert filter_set.count({"ids": [three_items[0].id, three_items[1].id]}) == 2
