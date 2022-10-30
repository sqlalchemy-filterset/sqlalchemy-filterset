import uuid
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.constants import EMPTY_VALUES
from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models.factories import Item


class ItemFilterSet(BaseFilterSet[Item]):
    id = Filter(Item.id)
    ids = InFilter(Item.id)


class TestFilterSetCountQuery(AssertsCompiledSQL):
    __dialect__: str = "default"

    async def test_count(self, async_session: AsyncSession) -> None:
        filter_set = ItemFilterSet(select(Item))
        self.assert_compile(filter_set.count_query({}), "SELECT count(1) AS count_1 FROM item")

    async def test_with_filter(self, async_session: AsyncSession) -> None:
        filter_set = ItemFilterSet(select(Item))
        self.assert_compile(
            filter_set.count_query({"id": uuid.uuid4()}),
            "SELECT count(1) AS count_1 FROM item WHERE item.id = :id_1",
        )

    async def test_with_distinct(self, async_session: AsyncSession) -> None:
        filter_set = ItemFilterSet(select(Item).distinct())
        self.assert_compile(
            filter_set.count_query({}),
            "SELECT count(1) AS count_1 FROM (SELECT DISTINCT item.id AS id, item.date AS date, "
            "item.area AS area, item.is_active AS is_active, item.title AS title, "
            "item.parent_id AS parent_id FROM item) AS anon_1",
        )

    async def test_with_distinct_on(self, async_session: AsyncSession) -> None:
        query = select(Item).distinct(Item.title).order_by(Item.title, Item.date.desc())
        filter_set = ItemFilterSet(query)
        self.assert_compile(
            filter_set.count_query({}),
            "SELECT count(1) AS count_1 FROM (SELECT DISTINCT ON (item.title) item.id AS id, "
            "item.date AS date, item.area AS area, item.is_active AS is_active, "
            "item.title AS title, item.parent_id AS parent_id FROM item "
            "ORDER BY item.title, item.date DESC) AS anon_1",
            dialect="postgresql",
        )

    @pytest.mark.parametrize("empty_value", EMPTY_VALUES)
    @pytest.mark.parametrize("field", ["id", "ids"])
    async def test_empty_values(self, empty_value: Any, field: str) -> None:
        filter_set = ItemFilterSet(select(Item))
        self.assert_compile(
            filter_set.count_query({field: empty_value}),
            "SELECT count(1) AS count_1 FROM item",
        )

    async def test_wrong_field(self) -> None:
        filter_set = ItemFilterSet(select(Item))
        self.assert_compile(
            filter_set.count_query({"test": "test"}),
            "SELECT count(1) AS count_1 FROM item",
        )
