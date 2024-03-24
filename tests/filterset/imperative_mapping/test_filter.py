from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.filterset.imperative_mapping.conftest import person_table


class PersonFilterSet(BaseFilterSet):
    id = Filter(person_table.c.id)
    name = Filter(person_table.c.name)


class TestFilterSetImperativeMappingFilterQuery(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected_where",
        [
            ("id", 1, f"person.id = {1}"),
        ],
    )
    def test_filter_one_param(self, field: str, value: Any, expected_where: str) -> None:
        filter_set = PersonFilterSet(select(person_table.c.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query({field: value}),
            f"SELECT person.id FROM person WHERE {expected_where}",
            literal_binds=True,
        )
