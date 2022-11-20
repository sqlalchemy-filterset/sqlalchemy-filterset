from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter
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

    def test_with_filter(self) -> None:
        filter_ = Filter(
            Parent.name,
            strategy=RelationSubqueryExistsStrategy,
            strategy_onclause=Item.parent_id == Parent.id,
        )
        self.assert_compile(
            filter_.filter(select(Item.id), "test"),
            "SELECT item.id FROM item WHERE EXISTS "
            "(SELECT 1 FROM parent WHERE item.parent_id = parent.id AND parent.name = 'test')",
            literal_binds=True,
        )
