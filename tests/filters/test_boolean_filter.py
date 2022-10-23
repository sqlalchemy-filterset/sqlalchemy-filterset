from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import BooleanFilter
from tests.models import Item


class TestBooleanFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [(True, "item.is_active IS 1"), (False, "item.is_active IS 0")],
    )
    def test_filtering(self, value: Any, expected_filtering: str) -> None:
        filter_ = BooleanFilter(Item.is_active)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    def test_no_filtering(self) -> None:
        filter_ = BooleanFilter(Item.is_active)
        stmt = filter_.filter(select(Item.id), None)
        self.assert_compile(stmt, "SELECT item.id FROM item")

    def test_no_filtering_with_exclude(self) -> None:
        filter_ = BooleanFilter(Item.is_active, exclude=True)
        stmt = filter_.filter(select(Item.id), None)
        self.assert_compile(stmt, "SELECT item.id FROM item")

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            (True, "item.is_active IS 1"),
            (False, "item.is_active IS 0"),
            (None, "item.is_active IS NULL"),
        ],
    )
    def test_filtering_with_nullable(self, value: Any, expected_filtering: str) -> None:
        filter_ = BooleanFilter(Item.is_active, nullable=True)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            (True, "item.is_active IS NOT 1"),
            (False, "item.is_active IS NOT 0"),
        ],
    )
    def test_filtering_with_exclude(self, value: Any, expected_filtering: str) -> None:
        filter_ = BooleanFilter(Item.is_active, exclude=True)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            (True, "item.is_active IS NOT 1"),
            (False, "item.is_active IS NOT 0"),
            (None, "item.is_active IS NOT NULL"),
        ],
    )
    def test_filtering_with_nullable_and_exclude(self, value: Any, expected_filtering: str) -> None:
        filter_ = BooleanFilter(Item.is_active, exclude=True, nullable=True)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")
