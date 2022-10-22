from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.constants import EMPTY_VALUES
from sqlalchemy_filterset.filters import SearchFilter
from tests.models import Item


class TestSearchBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_search(self) -> None:
        filter_ = SearchFilter(Item.title)
        stmt = filter_.filter(select(Item.id), "test")
        self.assert_compile(
            stmt,
            f"SELECT item.id FROM item WHERE lower(item.title) LIKE lower(:title_1)",
        )

    @pytest.mark.parametrize(
        "exclude, expected",
        [
            (True, "WHERE lower(item.title) NOT LIKE lower(:title_1)"),
            (False, "WHERE lower(item.title) LIKE lower(:title_1)"),
        ],
    )
    def test_exclude(self, exclude: bool, expected: str) -> None:
        filter_ = SearchFilter(Item.title, exclude=exclude)
        stmt = filter_.filter(select(Item.id), "test")
        self.assert_compile(stmt, f"SELECT item.id FROM item {expected}")

    @pytest.mark.parametrize("value", EMPTY_VALUES)
    def test_with_empty_value(self, value: Any) -> None:
        filter_ = SearchFilter(Item.title)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, "SELECT item.id FROM item")

    def test_search_with_many_fields(self) -> None:
        filter_ = SearchFilter(Item.title, Item.name)
        stmt = filter_.filter(select(Item.id), "test")
        self.assert_compile(
            stmt,
            "SELECT item.id FROM item "
            "WHERE lower(item.title) LIKE lower(:title_1) OR lower(item.name) LIKE lower(:name_1)",
        )
