from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import MethodFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models import Item


class TestMethodFilterSet(BaseFilterSet):
    area = MethodFilter(method="filter_area")

    @staticmethod
    def filter_area(query: Select, value: int) -> Select:
        return query.where(Item.area == value)


class TestInitMethodFilterInFilterSet:
    def test_init(self) -> None:
        filter_set = TestMethodFilterSet(query=select(Item.id))
        method_filter = filter_set.filters["area"]
        assert isinstance(method_filter, MethodFilter)
        assert method_filter.field_name == "area"
        assert method_filter.method == "filter_area"
        assert method_filter.filter_set == filter_set
        assert method_filter._filter == TestMethodFilterSet.filter_area

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
        filter_set = TestMethodFilterSet(query=select(Item.id))
        filter_ = filter_set.filters["area"]
        stmt = filter_.filter(filter_set.get_base_query(), value)
        self.assert_compile(stmt, "SELECT item.id FROM item WHERE item.area = :area_1")

    @pytest.mark.parametrize("value", [None, "", [], (), {}])
    def test_no_filtering(self, value: Any) -> None:
        filter_set = TestMethodFilterSet(query=select(Item.id))
        filter_ = filter_set.filters["area"]
        stmt = filter_.filter(filter_set.get_base_query(), value)
        self.assert_compile(stmt, "SELECT item.id FROM item")
