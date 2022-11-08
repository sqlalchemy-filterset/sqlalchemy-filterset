import operator as op
from typing import Any

import pytest
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import RangeFilter
from tests.models import Item


class TestRangeFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, left_lookup_expr, right_lookup_expr, logic_expr, value, expected",
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
        left_lookup_expr: Any,
        right_lookup_expr: Any,
        logic_expr: Any,
        value: Any,
        expected: str,
    ) -> None:
        filter_ = RangeFilter(
            field,
            left_lookup_expr=left_lookup_expr,
            right_lookup_expr=right_lookup_expr,
            logic_expr=logic_expr,
        )
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )

    @pytest.mark.parametrize("value", [None, [], [None, None]])
    def test_no_filtering(self, value: Any) -> None:
        filter_ = RangeFilter(Item.area)
        self.assert_compile(filter_.filter(select(Item.id), value), "SELECT item.id FROM item")
