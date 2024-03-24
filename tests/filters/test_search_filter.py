from typing import Any, Sequence

import pytest
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.sql import operators as sa_op
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import SearchFilter
from sqlalchemy_filterset.operators import icontains
from sqlalchemy_filterset.types import LookupExpr, ModelAttribute
from tests.models.base import Item


class TestSearchFilterBuildSelect(AssertsCompiledSQL):

    __dialect__ = "default"

    @pytest.mark.parametrize(
        "logic_expr, expected_logic",
        [
            (sa.and_, "AND"),
            (sa.or_, "OR"),
        ],
    )
    @pytest.mark.parametrize(
        "fields, lookup_expr, value, expected",
        [
            (
                [Item.name, Item.description],
                icontains,
                "foo",
                "lower(item.name) LIKE lower('%foo%') {}"
                " lower(item.description) LIKE lower('%foo%')",
            ),
            (
                [Item.name, Item.description],
                sa_op.like_op,
                "foo",
                "item.name LIKE 'foo' {} item.description LIKE 'foo'",
            ),
            (
                [Item.name, Item.description],
                sa_op.not_like_op,
                "foo",
                "item.name NOT LIKE 'foo' {} item.description NOT LIKE 'foo'",
            ),
            (
                [Item.name, Item.description],
                sa_op.ilike_op,
                "foo",
                "lower(item.name) LIKE lower('foo') {}"
                " lower(item.description) LIKE lower('foo')",
            ),
            (
                [Item.name, Item.description],
                sa_op.not_ilike_op,
                "foo",
                "lower(item.name) NOT LIKE lower('foo') {}"
                " lower(item.description) NOT LIKE lower('foo')",
            ),
            (
                [Item.name, Item.description],
                sa_op.startswith_op,
                "foo",
                "(item.name LIKE 'foo' || '%') {} (item.description LIKE 'foo' || '%')",
            ),
            (
                [Item.name, Item.description],
                sa_op.not_startswith_op,
                "foo",
                "(item.name NOT LIKE 'foo' || '%') {} (item.description NOT LIKE 'foo' || '%')",
            ),
            (
                [Item.name, Item.description],
                sa_op.endswith_op,
                "foo",
                "(item.name LIKE '%' || 'foo') {} (item.description LIKE '%' || 'foo')",
            ),
            (
                [Item.name, Item.description],
                sa_op.not_endswith_op,
                "foo",
                "(item.name NOT LIKE '%' || 'foo') {} (item.description NOT LIKE '%' || 'foo')",
            ),
            (
                [Item.name, Item.description],
                sa_op.contains_op,
                "foo",
                "(item.name LIKE '%' || 'foo' || '%') {}"
                " (item.description LIKE '%' || 'foo' || '%')",
            ),
            (
                [Item.name, Item.description],
                sa_op.not_contains_op,
                "foo",
                "(item.name NOT LIKE '%' || 'foo' || '%') {}"
                " (item.description NOT LIKE '%' || 'foo' || '%')",
            ),
        ],
    )
    def test_filtering(
        self,
        fields: Sequence[ModelAttribute],
        lookup_expr: LookupExpr,
        logic_expr: LookupExpr,
        value: str,
        expected: str,
        expected_logic: str,
    ) -> None:
        filter_ = SearchFilter(*fields, lookup_expr=lookup_expr, logic_expr=logic_expr)
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_.filter(select(Item.id), value, {}),
            f"SELECT item.id FROM item WHERE {expected.format(expected_logic)}",
            literal_binds=True,
        )

    @pytest.mark.parametrize("value", [None, ""])
    def test_no_filtering(self, value: Any) -> None:
        filter_ = SearchFilter(Item.name, Item.description)
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_.filter(select(Item.id), value, {}),
            "SELECT item.id FROM item",
            literal_binds=True,
        )
