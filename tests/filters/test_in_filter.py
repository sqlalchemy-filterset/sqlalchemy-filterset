from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import InFilter, NotInFilter
from tests.models.base import Item, ItemType


class TestInFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected",
        [
            (Item.name, ["foo"], "item.name IN ('foo')"),
            (Item.name, [""], "item.name IN ('')"),
            (Item.type, [ItemType.foo], "item.type IN ('foo')"),
            (Item.name, [ItemType.foo.value], "item.name IN ('foo')"),
            (Item.name, ["foo", "bar"], "item.name IN ('foo', 'bar')"),
            (Item.name, [], "item.name IN (NULL) AND (1 != 1)"),
            (Item.name, (), "item.name IN (NULL) AND (1 != 1)"),
        ],
    )
    def test_filtering(self, field: QueryableAttribute, value: Any, expected: str) -> None:
        filter_ = InFilter(field)
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_.filter(select(Item.id), value, {}),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )


class TestNotInFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected",
        [
            (Item.name, ["foo"], "(item.name NOT IN ('foo'))"),
            (Item.name, [""], "(item.name NOT IN (''))"),
            (Item.type, [ItemType.foo], "(item.type NOT IN ('foo'))"),
            (Item.name, [ItemType.foo.value], "(item.name NOT IN ('foo'))"),
            (Item.name, ["foo", "bar"], "(item.name NOT IN ('foo', 'bar'))"),
            (Item.name, [], "(item.name NOT IN (NULL) OR (1 = 1))"),
            (Item.name, (), "(item.name NOT IN (NULL) OR (1 = 1))"),
        ],
    )
    def test_filtering(self, field: QueryableAttribute, value: Any, expected: str) -> None:
        filter_ = NotInFilter(field)
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_.filter(select(Item.id), value, {}),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )
