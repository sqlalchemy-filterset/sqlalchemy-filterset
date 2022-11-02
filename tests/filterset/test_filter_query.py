import uuid
from typing import Any, Dict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.constants import EMPTY_VALUES
from sqlalchemy_filterset.filters import Filter, InFilter, SearchFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models import Item


class ItemFilterSet(BaseFilterSet[Item]):
    id = Filter(Item.id)
    ids = InFilter(Item.id)
    title = SearchFilter(Item.title)


class TestFilterSetFilterQuery(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected_where",
        [
            ("id", uuid.uuid4(), "item.id = :id_1"),
            ("ids", [uuid.uuid4()], "item.id IN (__[POSTCOMPILE_id_1])"),
            ("title", "test", "lower(item.title) LIKE lower(:title_1)"),
        ],
    )
    def test_filter_one_param(self, field: str, value: Any, expected_where: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(
            filter_set.filter_query({field: value}),
            "SELECT item.id " f"FROM item WHERE {expected_where}",
        )

    @pytest.mark.parametrize(
        "params, expected_where",
        [
            (
                {"id": uuid.uuid4(), "ids": [uuid.uuid4()], "title": "test"},
                "item.id = :id_1 AND item.id IN (__[POSTCOMPILE_id_2]) "
                "AND lower(item.title) LIKE lower(:title_1)",
            ),
        ],
    )
    def test_filter_multiple_param(self, params: Dict[str, Any], expected_where: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(
            filter_set.filter_query(params),
            f"SELECT item.id FROM item WHERE {expected_where}",
        )

    @pytest.mark.parametrize("empty_value", EMPTY_VALUES)
    @pytest.mark.parametrize("field", ["id", "ids", "title"])
    async def test_empty_values(
        self, empty_value: Any, field: str, async_session: AsyncSession
    ) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(
            filter_set.filter_query({field: empty_value}),
            "SELECT item.id FROM item",
        )

    async def test_wrong_field(self) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(
            filter_set.filter_query({"test": "test"}),
            "SELECT item.id FROM item",
        )
