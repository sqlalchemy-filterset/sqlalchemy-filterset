from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationInnerJoinedStrategy
from tests.models import Item, Parent


class TestRelationInnerJoinedStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = RelationInnerJoinedStrategy(Parent.name)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_onclause(self) -> None:
        strategy = RelationInnerJoinedStrategy(Parent.name, Item.id == Parent.id)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON item.id = parent.id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing(self) -> None:
        strategy = RelationInnerJoinedStrategy(Parent.name)
        self.assert_compile(
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )
