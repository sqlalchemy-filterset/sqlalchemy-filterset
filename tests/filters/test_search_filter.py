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

    @pytest.mark.parametrize("value", ["test", ""])
    @pytest.mark.parametrize("nullable", [False, True])
    def test_nullable(self, value: str, nullable: bool) -> None:
        filter_ = SearchFilter(Item.title, nullable=nullable)
        stmt = filter_.filter(select(Item.id), value)
        select_query = "SELECT item.id FROM item"
        if not nullable and value in EMPTY_VALUES:
            self.assert_compile(stmt, select_query)
        else:
            self.assert_compile(
                stmt, f"{select_query} WHERE lower(item.title) LIKE lower(:title_1)"
            )

    def test_search_with_many_fields(self) -> None:
        filter_ = SearchFilter(Item.title, Item.name)
        stmt = filter_.filter(select(Item.id), "test")
        self.assert_compile(
            stmt,
            "SELECT item.id FROM item "
            "WHERE lower(item.title) LIKE lower(:title_1) OR lower(item.name) LIKE lower(:name_1)",
        )
