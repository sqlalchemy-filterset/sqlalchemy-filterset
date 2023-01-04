from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationOuterJoinStrategy
from tests.models import Item, Parent


class TestRelationOuterJoinStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent.name)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item LEFT OUTER JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_onclause(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent.name, Item.id == Parent.id)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item LEFT OUTER JOIN parent "
            "ON item.id = parent.id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent.name, Item.parent_id == Parent.id)
        self.assert_compile(
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_without_onclause(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent.name)
        self.assert_compile(
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "LEFT OUTER JOIN parent ON parent.id = item.parent_id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_with_different_onclause(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent.name, onclause=Parent.id == Item.id)
        self.assert_compile(
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "LEFT OUTER JOIN parent ON parent.id = item.id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )
