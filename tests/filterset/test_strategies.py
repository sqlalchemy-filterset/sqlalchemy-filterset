import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.filtersets import BaseFilterSet
from sqlalchemy_filterset.strategies import RelationJoinStrategy, RelationSubqueryExistsStrategy
from tests.models.base import GrandParent, Item, Parent


class ItemFilterSetJoins(BaseFilterSet[Item]):
    parent_name = Filter(
        Parent.name, strategy=RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
    )
    grand_parent_name = Filter(
        GrandParent.name,
        strategy=RelationJoinStrategy(GrandParent, onclause=GrandParent.id == Item.grand_parent_id),
    )
    parent_date = Filter(
        Parent.date, strategy=RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
    )


class TestFilterSetJoinStrategies(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, expected_query",
        [
            (
                "parent_name",
                "SELECT item.id FROM item "
                "JOIN parent ON parent.id = item.parent_id WHERE parent.name = 'test'",
            ),
            (
                "grand_parent_name",
                "SELECT item.id FROM item JOIN grand_parent "
                "ON grand_parent.id = item.grand_parent_id WHERE grand_parent.name = 'test'",
            ),
        ],
    )
    def test_filter_one_param(self, field: str, expected_query: str) -> None:
        filter_set = ItemFilterSetJoins(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query({field: "test"}),
            expected_query,
            literal_binds=True,
        )

    def test_multiple(self) -> None:
        filter_set = ItemFilterSetJoins(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query(
                {"parent_name": "test_name", "grand_parent_name": "test_grand_name"}
            ),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "JOIN grand_parent ON grand_parent.id = item.grand_parent_id "
            "WHERE parent.name = 'test_name' AND grand_parent.name = 'test_grand_name'",
            literal_binds=True,
        )

    def test_deduplication(self) -> None:
        filter_set = ItemFilterSetJoins(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query({"parent_name": "test_name", "parent_date": "test_date"}),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "WHERE parent.name = 'test_name' AND parent.date = 'test_date'",
            literal_binds=True,
        )


class ItemFilterSetSubqueries(BaseFilterSet[Item]):
    parent_name = Filter(
        Parent.name,
        strategy=RelationSubqueryExistsStrategy(Parent, onclause=Parent.id == Item.parent_id),
    )
    grand_parent_name = Filter(
        GrandParent.name,
        strategy=RelationSubqueryExistsStrategy(
            GrandParent, onclause=GrandParent.id == Item.grand_parent_id
        ),
    )
    parent_date = Filter(
        Parent.date,
        strategy=RelationSubqueryExistsStrategy(Parent, onclause=Parent.id == Item.parent_id),
    )


class TestFilterSetSubqueryStrategies(AssertsCompiledSQL):
    __dialect__: str = "default"

    @pytest.mark.parametrize(
        "field, expected_query",
        [
            (
                "parent_name",
                "SELECT item.id FROM item WHERE EXISTS "
                "(SELECT 1 FROM parent WHERE parent.id = item.parent_id AND parent.name = 'test')",
            ),
            (
                "grand_parent_name",
                "SELECT item.id FROM item WHERE EXISTS "
                "(SELECT 1 FROM grand_parent "
                "WHERE grand_parent.id = item.grand_parent_id AND grand_parent.name = 'test')",
            ),
        ],
    )
    def test_filter_one_param(self, field: str, expected_query: str) -> None:
        filter_set = ItemFilterSetSubqueries(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query({field: "test"}),
            expected_query,
            literal_binds=True,
        )

    def test_multiple(self) -> None:
        filter_set = ItemFilterSetSubqueries(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query({"parent_name": "name", "grand_parent_name": "g_name"}),
            "SELECT item.id FROM item WHERE (EXISTS "
            "(SELECT 1 FROM parent WHERE parent.id = item.parent_id AND parent.name = 'name')) "
            "AND (EXISTS "
            "(SELECT 1 FROM grand_parent "
            "WHERE grand_parent.id = item.grand_parent_id AND grand_parent.name = 'g_name'))",
            literal_binds=True,
        )

    def test_deduplication(self) -> None:
        filter_set = ItemFilterSetSubqueries(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            filter_set.filter_query({"parent_name": "name", "parent_date": "date"}),
            "SELECT item.id FROM item WHERE "
            "EXISTS (SELECT 1 FROM parent WHERE parent.id = item.parent_id "
            "AND parent.name = 'name' AND parent.date = 'date')",
            literal_binds=True,
        )
