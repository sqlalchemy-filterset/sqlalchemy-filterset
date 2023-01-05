from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationSubqueryExistsStrategy
from tests.models import GrandParent, Item, Parent


class TestRelationSubqueryExistsStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent, Item.parent_id == Parent.id)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent WHERE item.parent_id = parent.id AND parent.name = 'test')",
            literal_binds=True,
        )

    def test_double_exist_preventing(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent, Item.parent_id == Parent.id)
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
        strategy = RelationSubqueryExistsStrategy(Parent, Item.parent_id == Parent.id)
        first = strategy.filter(select(Item.id), Parent.name == "test")
        strategy1 = RelationSubqueryExistsStrategy(Parent, Parent.id == Item.parent_id)
        res = strategy1.filter(first, Parent.name != "test1")
        self.assert_compile(
            res,
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent "
            "WHERE item.parent_id = parent.id AND parent.name = 'test' AND parent.name != 'test1')",
            literal_binds=True,
        )

    def test_double_exist_with_different_onclause(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent, Item.parent_id == Parent.id)
        first = strategy.filter(select(Item.id), Parent.name == "test")
        strategy1 = RelationSubqueryExistsStrategy(Parent, Item.parent_id != Parent.id)
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

    def test_exist_with_not_matched_exist(self) -> None:
        strategy = RelationSubqueryExistsStrategy(Parent, Item.parent_id == Parent.id)
        base_query = select(Item.id).where(
            select(GrandParent).where(GrandParent.id == Item.id).exists()
        )
        self.assert_compile(
            strategy.filter(base_query, Parent.name == "test"),
            "SELECT item.id FROM item "
            "WHERE "
            "(EXISTS (SELECT grand_parent.id, grand_parent.parent_id, grand_parent.name "
            "FROM grand_parent WHERE grand_parent.id = item.id)) "
            "AND "
            "(EXISTS (SELECT 1 FROM parent "
            "WHERE item.parent_id = parent.id AND parent.name = 'test'))",
            literal_binds=True,
        )
