import uuid
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import ArgumentError
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models.base import Item


class ItemFilterSet(BaseFilterSet[Item]):
    id = Filter(Item.id)
    ids = InFilter(Item.id)


class TestFilterSetCountQuery(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_count(self) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.count_query({}), "SELECT count(1) AS count_1 FROM item"
        )

    def test_with_filter(self) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.count_query({"id": uuid.uuid4()}),
            "SELECT count(1) AS count_1 FROM item WHERE item.id = :id_1",
        )

    def test_with_distinct(self) -> None:
        filter_set = ItemFilterSet(select(Item.id, Item.date).distinct())
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.count_query({}),
            "SELECT count(1) AS count_1 FROM (SELECT DISTINCT item.id AS id, item.date AS date "
            "FROM item) AS anon_1",
        )

    def test_with_distinct_on(self) -> None:
        query = (
            select(Item.id, Item.title).distinct(Item.title).order_by(Item.title, Item.date.desc())
        )
        filter_set = ItemFilterSet(query)
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.count_query({}),
            "SELECT count(1) AS count_1 FROM (SELECT DISTINCT ON (item.title) item.id AS id, "
            "item.title AS title FROM item "
            "ORDER BY item.title, item.date DESC) AS anon_1",
            dialect="postgresql",
        )

    @pytest.mark.parametrize("empty_value", ([], (), {}))
    @pytest.mark.parametrize("field", ["id", "ids"])
    def test_empty_values_v1_incompatibility(self, empty_value: Any, field: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        with pytest.raises(AssertionError):
            self.assert_compile(  # type: ignore[no-untyped-call]
                filter_set.count_query({field: empty_value}),
                "SELECT count(1) AS count_1 FROM item",
            )

    @pytest.mark.parametrize("empty_value", ("", None))
    @pytest.mark.parametrize("field", ["ids"])
    def test_empty_values_list_v1_incompatibility(self, empty_value: Any, field: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        with pytest.raises(ArgumentError):
            self.assert_compile(  # type: ignore[no-untyped-call]
                filter_set.count_query({field: empty_value}),
                "SELECT count(1) AS count_1 FROM item",
            )

    def test_wrong_field(self) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.count_query({"test": "test"}),
            "SELECT count(1) AS count_1 FROM item",
        )
