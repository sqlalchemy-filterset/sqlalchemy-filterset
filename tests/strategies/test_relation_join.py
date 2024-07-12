from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import RelationJoinStrategy
from tests.models.base import Item, Parent


class TestRelationInnerJoinStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_apply(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        query = strategy.apply(select(Item.id))
        self.assert_compile(  # type: ignore[no-untyped-call]
            query,
            "SELECT item.id FROM item JOIN parent " "ON parent.id = item.parent_id",
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
