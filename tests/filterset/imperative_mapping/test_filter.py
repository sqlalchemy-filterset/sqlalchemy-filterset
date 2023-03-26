from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from tests.filterset.imperative_mapping.conftest import Person


class PersonFilterSet(BaseFilterSet[Person]):
    id = Filter(Person.id)
    name = Filter(Person.name)


class TestFilterSetImperativeMappingFilterQuery(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, value, expected_where",
        [
            ("id", 1, f"person.id = {1}"),
        ],
    )
    def test_filter_one_param(self, field: str, value: Any, expected_where: str) -> None:
        filter_set = PersonFilterSet(select(Person.id))
        self.assert_compile(
            filter_set.filter_query({field: value}),
            f"SELECT person.id FROM person WHERE {expected_where}",
            literal_binds=True,
        )
