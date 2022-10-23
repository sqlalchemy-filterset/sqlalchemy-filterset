import operator as op
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import RangeFilter
from tests.models import Item


class TestRangeFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            ([1, 10], "item.area >= :area_1 AND item.area <= :area_2"),
            ((10, 1), "item.area >= :area_1 AND item.area <= :area_2"),
            ((None, 1), "item.area <= :area_1"),
            ((1, None), "item.area >= :area_1"),
        ],
    )
    def test_filtering(self, value: Any, expected_filtering: str) -> None:
        filter_ = RangeFilter(Item.area)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            ([1, 10], "item.area <= :area_1 OR item.area >= :area_2"),
            ((10, 1), "item.area <= :area_1 OR item.area >= :area_2"),
            ((None, 1), "item.area >= :area_1"),
            ((1, None), "item.area <= :area_1"),
        ],
    )
    def test_exclude(self, value: Any, expected_filtering: str) -> None:
        filter_ = RangeFilter(Item.area, exclude=True)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            ([1, 10], "item.area > :area_1 AND item.area < :area_2"),
            ((None, 1), "item.area < :area_1"),
            ((1, None), "item.area > :area_1"),
        ],
    )
    def test_filtering_with_operator(self, value: Any, expected_filtering: str) -> None:
        filter_ = RangeFilter(Item.area, min_operator=op.gt, max_operator=op.lt)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    @pytest.mark.parametrize(
        "value, expected_filtering",
        [
            ([1, 10], "item.area <= :area_1 OR item.area > :area_2"),
            ((None, 1), "item.area > :area_1"),
            ((1, None), "item.area <= :area_1"),
        ],
    )
    def test_filtering_with_operator_and_exclude(self, value: Any, expected_filtering: str) -> None:
        filter_ = RangeFilter(Item.area, min_operator=op.gt, exclude=True)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item WHERE {expected_filtering}")

    @pytest.mark.parametrize("value", [None, [], [None, None]])
    def test_no_filtering(self, value: Any) -> None:
        filter_ = RangeFilter(Item.area)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, f"SELECT item.id FROM item")

    def test_filtering_more_than_two_values_ignored(self) -> None:
        filter_ = RangeFilter(Item.area)
        stmt = filter_.filter(select(Item.id), [1, 2, 3, 4])
        self.assert_compile(
            stmt, f"SELECT item.id FROM item WHERE item.area >= :area_1 AND item.area <= :area_2"
        )

    def test_error_incorrect_operator(self) -> None:
        with pytest.raises(AssertionError):
            RangeFilter(Item.area, max_operator=op.eq)
        with pytest.raises(AssertionError):
            RangeFilter(Item.area, min_operator=op.eq)
