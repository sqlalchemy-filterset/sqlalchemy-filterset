import operator
from typing import Dict, List, Type

import pytest
from sqlalchemy import select
from sqlalchemy.sql import operators as sa_op

from sqlalchemy_filterset.filters import BaseFilter, Filter, RangeFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.models import Item


class FirstFilterSet(BaseFilterSet):
    id = Filter(Item.id)
    title = Filter(Item.title)

    some_attr = "Some attr"


class SecondInheritedFilterSet(FirstFilterSet):
    ids = Filter(Item.id, lookup_expr=sa_op.in_op)
    area = RangeFilter(Item.area)


class ThirdInheritedFilterSet(SecondInheritedFilterSet):
    other_id = Filter(Item.id)


class OverrideInheritedFilterSet(FirstFilterSet):
    id = Filter(Item.id, lookup_expr=sa_op.in_op)


@pytest.mark.parametrize(
    "filter_set_class,expected_filters",
    [
        (FirstFilterSet, {"id": Filter, "title": Filter}),
        (
            SecondInheritedFilterSet,
            {"id": Filter, "title": Filter, "ids": Filter, "area": RangeFilter},
        ),
        (
            ThirdInheritedFilterSet,
            {"id": Filter, "title": Filter, "ids": Filter, "area": RangeFilter, "other_id": Filter},
        ),
        (OverrideInheritedFilterSet, {"id": Filter, "title": Filter}),
    ],
)
def test_filters_detection(
    filter_set_class: Type[BaseFilterSet],
    expected_filters: Dict[str, Type[BaseFilter]],
) -> None:
    base_query = select(Item.id)
    filter_set = filter_set_class(base_query)
    detected_filters = filter_set.get_filters()
    assert len(detected_filters) == len(expected_filters)

    for filter_name, expected_filter_type in expected_filters.items():
        assert isinstance(detected_filters.get(filter_name), expected_filter_type)

    assert detected_filters.get("some_attr") is None


@pytest.mark.parametrize(
    "filter_set_class,expected_order",
    [
        (FirstFilterSet, ["id", "title"]),
        (SecondInheritedFilterSet, ["id", "title", "ids", "area"]),
        (ThirdInheritedFilterSet, ["id", "title", "ids", "area", "other_id"]),
        (OverrideInheritedFilterSet, ["id", "title"]),
    ],
)
async def test_inherited_filters_ordering(
    filter_set_class: Type[BaseFilterSet],
    expected_order: List[str],
) -> None:
    base_query = select(Item.id)
    filter_set = filter_set_class(base_query)
    detected_filters = filter_set.get_filters()

    assert list(detected_filters.keys()) == expected_order


@pytest.mark.parametrize(
    "filter_set_class",
    [
        FirstFilterSet,
        SecondInheritedFilterSet,
        ThirdInheritedFilterSet,
        OverrideInheritedFilterSet,
    ],
)
async def test_filter_field_name_set(filter_set_class: Type[BaseFilterSet]) -> None:
    filter_set = filter_set_class(select(Item.id))
    filters = filter_set.get_filters()
    for filter_name, filter_ in filters.items():
        assert filter_.field_name == filter_name


async def test_lookup_expr_overwritten() -> None:
    filter_ = FirstFilterSet(select(Item.id)).get_filters()["id"]
    overwritten_filter_ = OverrideInheritedFilterSet(select(Item.id)).get_filters()["id"]
    # todo: y.mezentsev investigate better compare lookup_expr in tests
    assert filter_.lookup_expr == operator.eq  # type: ignore
    assert overwritten_filter_.lookup_expr == sa_op.in_op  # type: ignore
