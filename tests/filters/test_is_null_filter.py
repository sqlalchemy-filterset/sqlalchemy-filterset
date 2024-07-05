from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import IsNullFilter
from tests.models.base import Item


class TestIsNullFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected",
        [
            (Item.name, True, "item.name IS NULL"),
            (Item.name, False, "item.name IS NOT NULL"),
            (Item.type, True, "item.type IS NULL"),
        ],
    )
    def test_filtering(self, field: QueryableAttribute, value: Any, expected: str) -> None:
        filter_ = IsNullFilter(field)
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_.filter(select(Item.id), value, {}),
            f"SELECT item.id FROM item WHERE {expected}",
            literal_binds=True,
        )
