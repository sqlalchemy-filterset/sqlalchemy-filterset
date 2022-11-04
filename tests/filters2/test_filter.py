import operator as op
from datetime import datetime
from functools import partial
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import operators as sa_op
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters2 import Filter
from tests.models import Item
from tests.models.base import ItemType


class TestFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, lookup_expr, value, expected",
        [
            (Item.area, op.eq, 1000, "item.area = 1000"),
            (Item.area, op.eq, "foo", "item.area = 'foo'"),
            (Item.area, op.eq, "", "item.area = ''"),
            (Item.type, op.eq, "foo", "item.type = 'foo'"),
            (Item.type, op.eq, ItemType.foo, "item.type = 'foo'"),
            (Item.name, op.eq, ItemType.foo.value, "item.name = 'foo'"),  # todo: strenum?
            (Item.area, op.eq, 0, "item.area = 0"),
            (Item.area, op.eq, None, "item.area IS NULL"),
            (Item.area, op.ne, 1000, "item.area != 1000"),
            (Item.area, op.ne, None, "item.area IS NOT NULL"),
            (Item.area, op.le, 1000, "item.area <= 1000"),
            (Item.area, op.le, 0, "item.area <= 0"),
            (Item.date, op.le, datetime(2000, 1, 1), "item.date <= '2000-01-01 00:00:00'"),
            (Item.area, op.lt, 1000, "item.area < 1000"),
            (Item.area, op.ge, 1000, "item.area >= 1000"),
            (Item.area, op.gt, 1000, "item.area > 1000"),
            (Item.name, sa_op.in_op, ["foo"], "item.name IN ('foo')"),
            (Item.name, sa_op.in_op, [""], "item.name IN ('')"),
            (Item.type, sa_op.in_op, [ItemType.foo], "item.type IN ('foo')"),
            (Item.name, sa_op.in_op, [ItemType.foo.value], "item.name IN ('foo')"),  # todo: strenum
            (Item.name, sa_op.in_op, ["foo", "bar"], "item.name IN ('foo', 'bar')"),
            (Item.name, sa_op.in_op, [], "item.name IN (NULL) AND (1 != 1)"),
            (Item.name, sa_op.in_op, (), "item.name IN (NULL) AND (1 != 1)"),
            (Item.name, sa_op.not_in_op, ["foo", "bar"], "(item.name NOT IN ('foo', 'bar'))"),
            (Item.name, sa_op.not_in_op, [], "(item.name NOT IN (NULL) OR (1 = 1))"),
            (Item.name, sa_op.not_in_op, (), "(item.name NOT IN (NULL) OR (1 = 1))"),
            (Item.is_active, sa_op.is_, True, "item.is_active IS 1"),
            (Item.is_active, sa_op.is_, False, "item.is_active IS 0"),
            (Item.is_active, sa_op.is_, None, "item.is_active IS NULL"),
            (Item.is_active, sa_op.is_not, True, "item.is_active IS NOT 1"),
            (Item.is_active, sa_op.is_not, False, "item.is_active IS NOT 0"),
            (Item.is_active, sa_op.is_not, None, "item.is_active IS NOT NULL"),
            (Item.name, sa_op.like_op, "foo", "item.name LIKE 'foo'"),
            (Item.name, sa_op.not_like_op, "foo", "item.name NOT LIKE 'foo'"),
            (Item.name, sa_op.like_op, "", "item.name LIKE ''"),
            (
                Item.name,
                partial(sa_op.like_op, escape="^"),
                "foo",
                "item.name LIKE 'foo' ESCAPE '^'",
            ),
            (
                Item.name,
                partial(sa_op.not_like_op, escape="^"),
                "foo",
                "item.name NOT LIKE 'foo' ESCAPE '^'",
            ),
            (Item.name, sa_op.ilike_op, "foo", "lower(item.name) LIKE lower('foo')"),
            (Item.name, sa_op.not_ilike_op, "foo", "lower(item.name) NOT LIKE lower('foo')"),
            (Item.name, sa_op.startswith_op, "foo", "(item.name LIKE 'foo' || '%')"),
            (Item.name, sa_op.not_startswith_op, "foo", "(item.name NOT LIKE 'foo' || '%')"),
            (Item.name, sa_op.endswith_op, "foo", "(item.name LIKE '%' || 'foo')"),
            (Item.name, sa_op.not_endswith_op, "foo", "(item.name NOT LIKE '%' || 'foo')"),
            (Item.name, sa_op.contains_op, "foo", "(item.name LIKE '%' || 'foo' || '%')"),
            (Item.name, sa_op.not_contains_op, "foo", "(item.name NOT LIKE '%' || 'foo' || '%')"),
            (
                Item.name,
                partial(sa_op.contains_op, escape="^", autoescape=True),
                "foo/%bar",
                "(item.name LIKE '%' || 'foo/^%bar' || '%' ESCAPE '^')",
            ),
        ],
    )
    def test_op_filtering(
        self, field: QueryableAttribute, lookup_expr: Any, value: Any, expected: str
    ) -> None:
        filter_ = Filter(field, lookup_expr=lookup_expr)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "value, lookup_expr",
        [
            (None, op.le),
            (None, op.lt),
            (None, op.ge),
            (None, op.gt),
            (None, sa_op.in_op),
            (None, sa_op.not_in_op),
            (None, sa_op.like_op),
            (None, sa_op.not_like_op),
            (None, sa_op.ilike_op),
            (None, sa_op.not_ilike_op),
            (None, sa_op.startswith_op),
            (None, sa_op.not_startswith_op),
            (None, sa_op.not_startswith_op),
            (None, sa_op.endswith_op),
            (None, sa_op.not_endswith_op),
            (None, sa_op.contains_op),
            (None, sa_op.not_contains_op),
        ],
    )
    def test_argument_error(self, value: Any, lookup_expr: Any) -> None:
        filter_ = Filter(Item.id, lookup_expr=lookup_expr)
        with pytest.raises(ArgumentError):
            filter_.filter(select(Item.id), value)