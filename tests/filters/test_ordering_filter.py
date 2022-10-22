from typing import List, Tuple

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import NullsPosition, OrderingField, OrderingFilter
from tests.models import Item


class TestOrderingField(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "ordering, reverse, expected",
        [
            (OrderingField(Item.area), False, "item.area ASC"),
            (OrderingField(Item.area), True, "item.area DESC"),
            (
                OrderingField(Item.area, nulls=NullsPosition.first),
                True,
                "item.area DESC NULLS FIRST",
            ),
            (OrderingField(Item.area, nulls=NullsPosition.last), True, "item.area DESC NULLS LAST"),
        ],
    )
    def test_build_sqlalchemy_field(
        self, ordering: OrderingField, reverse: bool, expected: str
    ) -> None:
        stmt = ordering.build_sqlalchemy_field(reverse)
        self.assert_compile(stmt, expected)


class TestOrderingBuildFields:
    @pytest.mark.parametrize(
        "input_param, expected",
        [
            ("area", (False, "area")),
            ("-area", (True, "area")),
            ("-", (True, "")),
            ("", (False, "")),
            ("error_value", (False, "error_value")),
        ],
    )
    def test_parse_param(self, input_param: str, expected: Tuple[bool, str]) -> None:
        filter_ = OrderingFilter(area=OrderingField(Item.area))
        reverse, param = filter_._parse_param(input_param)
        assert (reverse, param) == expected


class TestOrderingBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_no_ordering(self) -> None:
        filter_ = OrderingFilter(area=OrderingField(Item.area))
        stmt = filter_.filter(select(Item.id), [])
        self.assert_compile(stmt, "SELECT item.id FROM item")

    @pytest.mark.parametrize(
        "fields, expected_ordering",
        [
            (["area"], "item.area ASC"),
            (["-area"], "item.area DESC"),
            (["area", "date"], "item.area ASC, item.date ASC"),
            (["area", "-date"], "item.area ASC, item.date DESC"),
            (["-area", "date"], "item.area DESC, item.date ASC"),
            (["title", "date"], "item.title ASC NULLS LAST, item.date ASC"),
            (["-title", "is_active"], "item.title DESC NULLS LAST, item.is_active ASC NULLS FIRST"),
        ],
    )
    def test_ordering(self, fields: List[str], expected_ordering: str) -> None:
        filter_ = OrderingFilter(
            area=OrderingField(Item.area),
            date=OrderingField(Item.date),
            title=OrderingField(Item.title, nulls=NullsPosition.last),
            is_active=OrderingField(Item.is_active, nulls=NullsPosition.first),
        )
        stmt = filter_.filter(select(Item.id), fields)
        self.assert_compile(stmt, f"SELECT item.id FROM item ORDER BY {expected_ordering}")

    def test_non_defined_field(self) -> None:
        filter_ = OrderingFilter(area=OrderingField(Item.area))
        stmt = filter_.filter(select(Item.id), ["area", "test"])
        self.assert_compile(stmt, "SELECT item.id FROM item ORDER BY item.area ASC")

    def test_error_bad_value(self) -> None:
        filter_ = OrderingFilter(area=OrderingField(Item.area))
        stmt = filter_.filter(select(Item.id), ["-"])
        self.assert_compile(stmt, "SELECT item.id FROM item")

    def test_error_bad_value_non_defined_field(self) -> None:
        filter_ = OrderingFilter(area=OrderingField(Item.area))
        stmt = filter_.filter(select(Item.id), ["bad_value"])
        self.assert_compile(stmt, "SELECT item.id FROM item")

    def test_ordering_apply_order(self) -> None:
        filter_ = OrderingFilter(
            area=OrderingField(Item.area),
            date=OrderingField(Item.date),
            title=OrderingField(Item.title),
        )
        stmt = filter_.filter(select(Item.id), ["date", "title", "area"])
        self.assert_compile(
            stmt, "SELECT item.id FROM item ORDER BY item.date ASC, item.title ASC, item.area ASC"
        )
