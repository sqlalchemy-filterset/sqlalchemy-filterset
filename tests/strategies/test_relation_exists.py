import pytest
from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationSubqueryExistsStrategy
from tests.models import Item, Parent


class TestRelationSubqueryExistsStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent.name, Item.parent_id == Parent.id)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent WHERE item.parent_id = parent.id AND parent.name = 'test')",
            literal_binds=True,
        )

    def test_double_exist_preventing(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent.date, Item.parent_id == Parent.id)
        first = strategy.filter(select(Item.id), Parent.name == "test")
        res = strategy.filter(first, Parent.name != "test1")
        self.assert_compile(
            res,
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent "
            "WHERE item.parent_id = parent.id AND parent.name = 'test' AND parent.name != 'test1')",
            literal_binds=True,
        )

    def test_double_exist_with_preventing_with_reversed_onclause(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent.date, Item.parent_id == Parent.id)
        first = strategy.filter(select(Item.id), Parent.name == "test")
        strategy1 = RelationSubqueryExistsStrategy(Parent.date, Parent.id == Item.parent_id)
        res = strategy1.filter(first, Parent.name != "test1")
        self.assert_compile(
            res,
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent "
            "WHERE item.parent_id = parent.id AND parent.name = 'test' AND parent.name != 'test1')",
            literal_binds=True,
        )

    def test_double_exist_with_different_onclause(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent.date, Item.parent_id == Parent.id)
        first = strategy.filter(select(Item.id), Parent.name == "test")
        strategy1 = RelationSubqueryExistsStrategy(Parent.date, Item.parent_id != Parent.id)
        res = strategy1.filter(first, Parent.name != "test1")
        self.assert_compile(
            res,
            "SELECT item.id FROM item "
            "WHERE "
            "(EXISTS (SELECT 1 FROM parent "
            "WHERE item.parent_id = parent.id AND parent.name = 'test')) "
            "AND "
            "(EXISTS (SELECT 1 FROM parent "
            "WHERE item.parent_id != parent.id AND parent.name != 'test1'))",
            literal_binds=True,
        )

    def test_onclause_assert(self) -> None:
        with pytest.raises(AssertionError):
            RelationSubqueryExistsStrategy(Parent.name, None)
