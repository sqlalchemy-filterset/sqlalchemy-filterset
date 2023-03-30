from typing import Any, Dict

import pytest
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import BaseFilter, MethodFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models.base import Item


class CustomFilter(BaseFilter):
    def filter(self, query: Select, value: Any, values: Any) -> Select:
        title = values.get("title")
        if title:
            return query.where(Item.title == title)
        return query.where(Item.name == value)


class ItemFilterSet(BaseFilterSet[Item]):
    name = CustomFilter()
    name_method = MethodFilter(method="filter_custom_method")

    @staticmethod
    def filter_custom_method(query: Select, value: Any, values: Any) -> Select:
        title = values.get("title")
        if title:
            return query.where(Item.title == title)
        return query.where(Item.name == value)


class TestAccessValues(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "params, expected_where",
        [
            ({"name": "test", "title": "test2"}, "item.title = 'test2'"),
            ({"name": "test"}, "item.name = 'test'"),
            ({"name_method": "test", "title": "test2"}, "item.title = 'test2'"),
            ({"name_method": "test"}, "item.name = 'test'"),
        ],
    )
    def test_filtering(self, params: Dict, expected_where: str) -> None:
        filter_set = ItemFilterSet(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query(params),
            f"SELECT item.id FROM item WHERE {expected_where}",
            literal_binds=True,
        )
