from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import LimitOffsetFilter
from tests.models.base import Item


class TestRangeFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            ((0, 10), "LIMIT 0 OFFSET 10"),
            ((50, 100), "LIMIT 50 OFFSET 100"),
            ((None, 100), "LIMIT -1 OFFSET 100"),
            ((0, None), "LIMIT 0"),
        ],
    )
    def test_pagination(self, value: Any, expected_filtering: str) -> None:
        filter_ = LimitOffsetFilter()
        self.assert_compile(
            filter_.filter(select(Item.id), value, {}),
            f"SELECT item.id FROM item {expected_filtering}",
            literal_binds=True,
        )

    @pytest.mark.parametrize("value", [None, (), (None, None)])
    def test_no_pagination(self, value: Any) -> None:
        filter_ = LimitOffsetFilter()
        self.assert_compile(filter_.filter(select(Item.id), value, {}), "SELECT item.id FROM item")

    @pytest.mark.parametrize("value", [None, ()])
    def test_no_reset_existing_pagination(self, value: Any) -> None:
        filter_ = LimitOffsetFilter()
        self.assert_compile(
            filter_.filter(select(Item.id).limit(10).offset(10), value, {}),
            "SELECT item.id FROM item LIMIT 10 OFFSET 10",
            literal_binds=True,
        )

    def test_reset_existing_pagination(self) -> None:
        filter_ = LimitOffsetFilter()
        self.assert_compile(
            filter_.filter(select(Item.id).limit(10).offset(10), (None, None), {}),
            "SELECT item.id FROM item",
        )

    def test_reset_existing_limit(self) -> None:
        filter_ = LimitOffsetFilter()
        self.assert_compile(
            filter_.filter(select(Item.id).limit(10).offset(10), (None, 10), {}),
            "SELECT item.id FROM item LIMIT -1 OFFSET 10",
            literal_binds=True,
        )

    def test_reset_existing_offset(self) -> None:
        filter_ = LimitOffsetFilter()
        self.assert_compile(
            filter_.filter(select(Item.id).limit(10).offset(10), (10, None), {}),
            "SELECT item.id FROM item LIMIT 10",
            literal_binds=True,
        )
