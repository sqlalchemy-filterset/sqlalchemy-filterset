import uuid
from typing import Dict, List, Type

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.filters import BaseFilter, Filter, InFilter
from sqlalchemy_filterset.filterset import FilterSet
from tests.models import ItemForFilters


class FirstFilterSet(FilterSet):
    id = Filter(ItemForFilters, "id")
    title = Filter(ItemForFilters, "title")

    some_attr = "Some attr"


class SecondInheritedFilterSet(FirstFilterSet):
    ids = InFilter(ItemForFilters, "id")


class ThirdInheritedFilterSet(SecondInheritedFilterSet):
    other_id = Filter(ItemForFilters, "id")


class OverrideInheritedFilterSet(FirstFilterSet):
    id = InFilter(ItemForFilters, "id")


@pytest.mark.parametrize(
    "filter_set_class,expected_filters",
    [
        (FirstFilterSet, {"id": Filter, "title": Filter}),
        (SecondInheritedFilterSet, {"id": Filter, "title": Filter, "ids": InFilter}),
        (
            ThirdInheritedFilterSet,
            {"id": Filter, "title": Filter, "ids": InFilter, "other_id": Filter},
        ),
        (OverrideInheritedFilterSet, {"id": InFilter, "title": Filter}),
    ],
)
async def test_filters_detection(
    filter_set_class: Type[FilterSet],
    expected_filters: Dict[str, Type[BaseFilter]],
    db_session: AsyncSession,
) -> None:
    base_query = select(ItemForFilters)
    filter_set = filter_set_class({"id": uuid.uuid4()}, db_session, base_query)
    detected_filters = filter_set.get_filters()
    assert len(detected_filters) == len(expected_filters)

    for filter_name, expected_filter_type in expected_filters.items():
        assert isinstance(detected_filters.get(filter_name), expected_filter_type)

    assert detected_filters.get("some_attr") is None


@pytest.mark.parametrize(
    "filter_set_class,expected_order",
    [
        (FirstFilterSet, ["id", "title"]),
        (SecondInheritedFilterSet, ["id", "title", "ids"]),
        (ThirdInheritedFilterSet, ["id", "title", "ids", "other_id"]),
        (OverrideInheritedFilterSet, ["id", "title"]),
    ],
)
async def test_one_inherited_filters_ordering(
    filter_set_class: Type[FilterSet],
    expected_order: List[str],
    db_session: AsyncSession,
) -> None:
    base_query = select(ItemForFilters)
    filter_set = filter_set_class({"id": uuid.uuid4()}, db_session, base_query)
    detected_filters = filter_set.get_filters()

    assert list(detected_filters.keys()) == expected_order
