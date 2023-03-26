from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import MethodFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models.base import Item


class FilterSetClass(BaseFilterSet):
    name = MethodFilter(method="filter_name")
    area = MethodFilter(method="filter_area")
    type = MethodFilter(method="filter_type")

    @staticmethod
    def filter_area(query: Select, value: int) -> Select:
        return query.where(Item.area == value)

    @staticmethod
    def filter_name(query: Select, value: str) -> Select:
        return query.where(Item.name == value)

    @staticmethod
    def filter_type(query: Select, value: list) -> Select:
        return query.where(Item.type.in_(value))


class TestInitMethodFilterInFilterSet:
    def test_init(self) -> None:
        filter_set = FilterSetClass(query=select(Item.id))
        method_filter = filter_set.filters["area"]
        assert isinstance(method_filter, MethodFilter)
        assert method_filter.field_name == "area"
        assert method_filter.method == "filter_area"
        assert method_filter.filter_set == filter_set
        assert method_filter._filter == FilterSetClass.filter_area

    def test_method_filter_not_found(self) -> None:
        class ErrorFilterSet(BaseFilterSet):
            test = MethodFilter(method="filter_param_has_one_name")

            @staticmethod
            def filter_method_has_another_name(query: Select, value: Any) -> Select:
                return query  # pragma: no cover

        with pytest.raises(AssertionError):
            ErrorFilterSet(query=select(Item.id))


class TestMethodFilterBuildSelect(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize("value", [1000, 0])
    def test_filtering(self, value: Any) -> None:
        filter_set = FilterSetClass(query=select(Item.id))
        filter_ = filter_set.filters["area"]
        stmt = filter_.filter(filter_set.get_base_query(), value, {})
        self.assert_compile(
            stmt, f"SELECT item.id FROM item WHERE item.area = {value}", literal_binds=True
        )

    @pytest.mark.parametrize("value", ["foo", ""])
    def test_filtering_text(self, value: Any) -> None:
        filter_set = FilterSetClass(query=select(Item.id))
        filter_ = filter_set.filters["name"]
        stmt = filter_.filter(filter_set.get_base_query(), value, {})
        self.assert_compile(
            stmt, f"SELECT item.id FROM item WHERE item.name = '{value}'", literal_binds=True
        )

    def test_filtering_by_null(self) -> None:
        filter_set = FilterSetClass(query=select(Item.id))
        filter_ = filter_set.filters["name"]
        stmt = filter_.filter(filter_set.get_base_query(), None, {})
        self.assert_compile(stmt, "SELECT item.id FROM item WHERE item.name IS NULL")

    @pytest.mark.parametrize("value", [[], (), {}])
    def test_filtering_empty_sequence(self, value: Any) -> None:
        filter_set = FilterSetClass(query=select(Item.id))
        filter_ = filter_set.filters["type"]
        stmt = filter_.filter(filter_set.get_base_query(), value, {})
        self.assert_compile(
            stmt,
            "SELECT item.id FROM item WHERE item.type IN (NULL) AND (1 != 1)",
            literal_binds=True,
        )
