from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationJoinStrategy, RelationOuterJoinStrategy
from tests.models.base import GrandParent, Item, Parent


class TestRelationInnerJoinStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_apply(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        query = strategy.apply(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            query,
            "SELECT item.id FROM item JOIN parent ON parent.id = item.parent_id",
            literal_binds=True,
        )

    def test_filter(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        query = strategy.apply(select(Item.id))
        query = strategy.filter(query, Parent.name == "test")
        self.assert_compile(  # type: ignore[no-untyped-call]
            query,
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_eq(self) -> None:
        assert RelationJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        ) == RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        assert RelationJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        ) == RelationJoinStrategy(Parent, onclause=Item.parent_id == Parent.id)

        assert RelationJoinStrategy(
            GrandParent, onclause=GrandParent.id == Item.grand_parent_id
        ) != RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        assert RelationJoinStrategy(Parent, onclause=Parent.id == Item.id) != RelationJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        )


class TestRelationOuterJoinStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_apply(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        query = strategy.apply(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            query,
            "SELECT item.id FROM item LEFT OUTER JOIN parent ON parent.id = item.parent_id",
            literal_binds=True,
        )

    def test_filter(self) -> None:
        strategy = RelationOuterJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        query = strategy.apply(select(Item.id))
        query = strategy.filter(query, Parent.name == "test")
        self.assert_compile(  # type: ignore[no-untyped-call]
            query,
            "SELECT item.id FROM item LEFT OUTER JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_eq(self) -> None:
        assert RelationOuterJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        ) == RelationOuterJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        assert RelationOuterJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        ) == RelationOuterJoinStrategy(Parent, onclause=Item.parent_id == Parent.id)

        assert RelationOuterJoinStrategy(
            GrandParent, onclause=GrandParent.id == Item.grand_parent_id
        ) != RelationOuterJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        assert RelationOuterJoinStrategy(
            Parent, onclause=Parent.id == Item.id
        ) != RelationOuterJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)

        assert RelationJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        ) != RelationOuterJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        assert RelationJoinStrategy(
            Parent, onclause=Parent.id == Item.parent_id
        ) != RelationOuterJoinStrategy(Parent, onclause=Item.parent_id == Parent.id)
