from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import BooleanFilter
from tests.models.base import Item


class TestBooleanFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected",
        [
            (Item.is_active, True, "item.is_active IS 1"),
            (Item.is_active, False, "item.is_active IS 0"),
            (Item.is_active, None, "item.is_active IS NULL"),
        ],
    )
    def test_filtering(self, field: QueryableAttribute, value: Any, expected: str) -> None:
        filter_ = BooleanFilter(field)
        self.assert_compile(
            filter_.filter(select(Item.id), value, {}),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )
