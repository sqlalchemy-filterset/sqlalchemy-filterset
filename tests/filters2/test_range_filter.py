import operator as op
from typing import Any

import pytest
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters2 import RangeFilter
from tests.models import Item


class TestRangeFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, left_op, right_op, logic_op, value, expected",
        [
            (Item.area, op.ge, op.le, and_, (0, 10), "item.area >= 0 AND item.area <= 10"),
            (Item.area, op.ge, op.le, and_, (None, 10), "item.area <= 10"),
            (Item.area, op.ge, op.le, and_, (0, None), "item.area >= 0"),
            (Item.area, op.gt, op.le, and_, (0, 10), "item.area > 0 AND item.area <= 10"),
            (Item.area, op.ge, op.lt, and_, (0, 10), "item.area >= 0 AND item.area < 10"),
            (Item.area, op.gt, op.lt, and_, (0, 10), "item.area > 0 AND item.area < 10"),
            (Item.area, op.ge, op.le, or_, (None, 10), "item.area <= 10"),
            (Item.area, op.ge, op.le, or_, (0, None), "item.area >= 0"),
            (Item.area, op.le, op.ge, or_, (0, 10), "item.area <= 0 OR item.area >= 10"),
            (Item.area, op.lt, op.gt, or_, (0, 10), "item.area < 0 OR item.area > 10"),
        ],
    )
    def test_filtering(
        self,
        field: QueryableAttribute,
        left_op: Any,
        right_op: Any,
        logic_op: Any,
        value: Any,
        expected: str,
    ) -> None:
        filter_ = RangeFilter(field, left_op=left_op, right_op=right_op, logic_op=logic_op)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )

    @pytest.mark.parametrize("value", [None, [], [None, None]])
    def test_no_filtering(self, value: Any) -> None:
        filter_ = RangeFilter(Item.area)
        stmt = filter_.filter(select(Item.id), value)
        self.assert_compile(stmt, "SELECT item.id FROM item")
