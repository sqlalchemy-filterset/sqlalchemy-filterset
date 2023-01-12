import uuid
from typing import Any, Dict

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models import Item


class ItemFilterSet(BaseFilterSet[Item]):
    id = Filter(Item.id)
    ids = InFilter(Item.id)


class TestFilterSetFilterQuery(AssertsCompiledSQL):
    __dialect__: str = "default"
    uuid_1 = uuid.UUID("a11a9cf6-36fb-40bf-b845-a53393bc0c53")
    uuid_2 = uuid.UUID("c0fc637c-2c1d-4a3e-9f7b-d053f35a4b15")

    @pytest.mark.parametrize(
        "field, value, expected_where",
        [
            ("id", uuid_1, f"item.id = '{uuid_1}'"),
            ("ids", [uuid_2], f"item.id IN ('{uuid_2}')"),
        ],
    )
    def test_filter_one_param(self, field: str, value: Any, expected_where: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(
            filter_set.filter_query({field: value}),
            "SELECT item.id " f"FROM item WHERE {expected_where}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "params, expected_where",
        [
            ({"id": uuid_1, "ids": [uuid_2]}, f"item.id = '{uuid_1}' AND item.id IN ('{uuid_2}')"),
        ],
    )
    def test_filter_multiple_param(self, params: Dict[str, Any], expected_where: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(
            filter_set.filter_query(params),
            f"SELECT item.id FROM item WHERE {expected_where}",
            literal_binds=True,
        )

    @pytest.mark.xfail(reason="Empty values not available in V2")
    @pytest.mark.parametrize("empty_value", ([], (), {}, "", None))
    @pytest.mark.parametrize("field", ["id", "ids"])
    async def test_empty_values(self, empty_value: Any, field: str) -> None:
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
