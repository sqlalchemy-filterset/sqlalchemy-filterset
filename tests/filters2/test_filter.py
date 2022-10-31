import operator as op
from functools import partial
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.sql import operators as sa_op
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters2 import Filter
from tests.models import Item


class TestFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "value, lookup_expr, expected_filtering",
        [
            (1000, op.eq, "item.area = 1000"),
            (0, op.eq, "item.area = 0"),
            (1000, op.ne, "item.area != 1000"),
            (1000, op.le, "item.area <= 1000"),
            (1000, op.lt, "item.area < 1000"),
            (1000, op.ge, "item.area >= 1000"),
            (1000, op.gt, "item.area > 1000"),
        ],
    )
    def test_op_filtering(self, value: Any, lookup_expr: Any, expected_filtering: str) -> None:
        filter_ = Filter(Item.area, lookup_expr=lookup_expr)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected_filtering}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "value, lookup_expr",
        [
            ([], sa_op.in_op),
            (None, sa_op.in_op),
            ([], sa_op.not_in_op),
            (None, sa_op.not_in_op),
        ],
    )
    def test_op_no_filtering(self, value: Any, lookup_expr: Any) -> None:
        filter_ = Filter(Item.name, lookup_expr=lookup_expr)
        self.assert_compile(filter_.filter(select(Item.id), value), "SELECT item.id FROM item")

    @pytest.mark.parametrize(
        "value, lookup_expr, expected_filtering",
        [
            (None, op.eq, "item.area IS NULL"),
            (None, op.ne, "item.area IS NOT NULL"),
            # (None, op.le, "item.area IS NULL"),  # todo: not working with nullable
            # (None, op.lt, "item.area IS NULL"),  # todo: not working with nullable
            # (None, op.ge, "item.area IS NULL"),  # todo: not working with nullable
            # (None, op.gt, "item.area IS NULL"),  # todo: not working with nullable
        ],
    )
    def test_op_nullable_filtering(
        self, value: Any, lookup_expr: Any, expected_filtering: str
    ) -> None:
        filter_ = Filter(Item.area, lookup_expr=lookup_expr, nullable=True)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected_filtering}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "value, lookup_expr, expected_filtering",
        [
            (["test"], sa_op.in_op, "item.name IN ('test')"),
            (["test1", "test2"], sa_op.in_op, "item.name IN ('test1', 'test2')"),
            (["test1", "test2"], sa_op.not_in_op, "(item.name NOT IN ('test1', 'test2'))"),
        ],
    )
    def test_list_in_filtering(self, value: Any, lookup_expr: Any, expected_filtering: str) -> None:
        filter_ = Filter(Item.name, lookup_expr=lookup_expr)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected_filtering}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "value, lookup_expr",
        [
            ([], sa_op.in_op),
            (None, sa_op.in_op),
            ([], sa_op.not_in_op),
            (None, sa_op.not_in_op),
        ],
    )
    def test_list_in_no_filtering(self, value: Any, lookup_expr: Any) -> None:
        filter_ = Filter(Item.name, lookup_expr=lookup_expr)
        self.assert_compile(filter_.filter(select(Item.id), value), "SELECT item.id FROM item")

    # @pytest.mark.parametrize(
    #     "value, lookup_expr, expected_filtering",
    #     [
    #         (None, sa_op.in_op, "item.name IS NULL"),  # todo: not working with nullable
    #         ([], sa_op.in_op, "item.name IS NULL"),  # todo: not working with nullable
    #     ],
    # )
    # def test_list_in_nullable_filtering(
    #     self, value: Any, lookup_expr: Any, expected_filtering: str
    # ) -> None:
    #     filter_ = Filter(Item.name, lookup_expr=lookup_expr, nullable=True)
    #     self.assert_compile(
    #         filter_.filter(select(Item.id), value),
    #         f"SELECT item.id FROM item WHERE {expected_filtering}",
    #         literal_binds=True,
    #     )

    @pytest.mark.parametrize(
        "value, lookup_expr, expected_filtering",
        [
            (True, sa_op.is_, "item.is_active IS 1"),
            (False, sa_op.is_, "item.is_active IS 0"),
            (True, sa_op.is_not, "item.is_active IS NOT 1"),
            (False, sa_op.is_not, "item.is_active IS NOT 0"),
        ],
    )
    def test_is_filtering(self, value: Any, lookup_expr: Any, expected_filtering: str) -> None:
        filter_ = Filter(Item.is_active, lookup_expr=lookup_expr)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected_filtering}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "value, lookup_expr",
        [
            (None, sa_op.is_),
            (None, sa_op.is_not),
        ],
    )
    def test_list_is_no_filtering(self, value: Any, lookup_expr: Any) -> None:
        filter_ = Filter(Item.name, lookup_expr=lookup_expr)
        self.assert_compile(filter_.filter(select(Item.id), value), "SELECT item.id FROM item")

    @pytest.mark.parametrize(
        "value, lookup_expr, expected_filtering",
        [
            (None, sa_op.is_, "item.is_active IS NULL"),
            (None, sa_op.is_not, "item.is_active IS NOT NULL"),
        ],
    )
    def test_is_nullable_filtering(
        self, value: Any, lookup_expr: Any, expected_filtering: str
    ) -> None:
        filter_ = Filter(Item.is_active, lookup_expr=lookup_expr, nullable=True)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected_filtering}",
            literal_binds=True,
        )

    @pytest.mark.parametrize(
        "value, lookup_expr, expected_filtering",
        [
            ("foo", sa_op.like_op, "item.name LIKE 'foo'"),
            ("foo", sa_op.not_like_op, "item.name NOT LIKE 'foo'"),
            # ("", sa_op.like_op, "item.name LIKE ''"),  # todo: need nullable=True, not obvious
            ("foo", partial(sa_op.like_op, escape="^"), "item.name LIKE 'foo' ESCAPE '^'"),
            ("foo", partial(sa_op.not_like_op, escape="^"), "item.name NOT LIKE 'foo' ESCAPE '^'"),
            ("foo", sa_op.ilike_op, "lower(item.name) LIKE lower('foo')"),
            ("foo", sa_op.not_ilike_op, "lower(item.name) NOT LIKE lower('foo')"),
            ("foo", sa_op.startswith_op, "(item.name LIKE 'foo' || '%')"),
            ("foo", sa_op.not_startswith_op, "(item.name NOT LIKE 'foo' || '%')"),
            ("foo", sa_op.endswith_op, "(item.name LIKE '%' || 'foo')"),
            ("foo", sa_op.not_endswith_op, "(item.name NOT LIKE '%' || 'foo')"),
            ("foo", sa_op.contains_op, "(item.name LIKE '%' || 'foo' || '%')"),
            ("foo", sa_op.not_contains_op, "(item.name NOT LIKE '%' || 'foo' || '%')"),
            (
                "foo/%bar",
                partial(sa_op.contains_op, escape="^", autoescape=True),
                "(item.name LIKE '%' || 'foo/^%bar' || '%' ESCAPE '^')",
            ),
        ],
    )
    def test_text_filtering(self, value: Any, lookup_expr: Any, expected_filtering: str) -> None:
        filter_ = Filter(Item.name, lookup_expr=lookup_expr)
        self.assert_compile(
            filter_.filter(select(Item.id), value),
            f"SELECT item.id FROM item WHERE {expected_filtering}",
            literal_binds=True,
        )

    # @pytest.mark.parametrize(
    #     "value, lookup_expr, expected_filtering",
    #     [
    #         (None, sa_op.like_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.not_like_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.ilike_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.not_ilike_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.startswith_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.not_startswith_op, "item.name IS NULL"),  # todo: not working with null
    #         (None, sa_op.endswith_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.not_endswith_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.contains_op, "item.name IS NULL"),  # todo: not working with nullable
    #         (None, sa_op.not_contains_op, "item.name IS NULL"),  # todo: not working with nullable
    #     ],
    # )
    # def test_text_nullable_filtering(
    #     self, value: Any, lookup_expr: Any, expected_filtering: str
    # ) -> None:
    #     filter_ = Filter(Item.name, lookup_expr=lookup_expr, nullable=True)
    #     self.assert_compile(
    #         filter_.filter(select(Item.id), value),
    #         f"SELECT item.id FROM item WHERE {expected_filtering}",
    #         literal_binds=True,
    #     )
