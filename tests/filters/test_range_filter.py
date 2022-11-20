import operator as op
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import RangeFilter
from sqlalchemy_filterset.strategies import (
    BaseStrategy,
    RelationInnerJoinStrategy,
    RelationOuterJoinStrategy,
    RelationSubqueryExistsStrategy,
)
from tests.models import Item, Parent


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

    def test_base_strategy(self) -> None:
        filter_ = RangeFilter(Item.area, strategy=BaseStrategy)
        self.assert_compile(
            filter_.filter(select(Item.id), (0, 10)),
            "SELECT item.id FROM item WHERE item.area >= 0 AND item.area <= 10",
            literal_binds=True,
        )

    def test_subquery_exists_strategy(self) -> None:
        filter_ = RangeFilter(
            Parent.date,
            strategy=RelationSubqueryExistsStrategy,
            strategy_onclause=Item.parent_id == Parent.id,
        )
        self.assert_compile(
            filter_.filter(select(Item.id), (datetime(2000, 1, 1), datetime(2000, 1, 2))),
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent WHERE item.parent_id = parent.id "
            "AND parent.date >= '2000-01-01 00:00:00' AND parent.date <= '2000-01-02 00:00:00')",
            literal_binds=True,
        )

    def test_inner_join_strategy(self) -> None:
        filter_ = RangeFilter(Parent.date, strategy=RelationInnerJoinStrategy)
        self.assert_compile(
            filter_.filter(select(Item.id), (datetime(2000, 1, 1), datetime(2000, 1, 2))),
            "SELECT item.id FROM item JOIN parent ON parent.id = item.parent_id "
            "WHERE parent.date >= '2000-01-01 00:00:00' AND parent.date <= '2000-01-02 00:00:00'",
            literal_binds=True,
        )

    def test_outer_join_strategy(self) -> None:
        filter_ = RangeFilter(Parent.date, strategy=RelationOuterJoinStrategy)
        self.assert_compile(
            filter_.filter(select(Item.id), (datetime(2000, 1, 1), datetime(2000, 1, 2))),
            "SELECT item.id FROM item LEFT OUTER JOIN parent ON parent.id = item.parent_id "
            "WHERE parent.date >= '2000-01-01 00:00:00' AND parent.date <= '2000-01-02 00:00:00'",
            literal_binds=True,
        )
