from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationJoinStrategy
from tests.models.base import GrandParent, Item, Parent


class TestRelationInnerJoinStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Item.parent_id == Parent.id)
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing_multiple_joins(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Item.parent_id == Parent.id)
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id)
                .join(Parent, onclause=Item.parent_id == Parent.id)
                .join(GrandParent, onclause=Item.grand_parent_id == GrandParent.id),
                Parent.name == "test",
            ),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "JOIN grand_parent ON grand_parent.id = item.grand_parent_id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_with_different_onclause(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.id)
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "JOIN parent ON parent.id = item.id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )
