from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.strategies import RelationOuterJoinedStrategy
from tests.models import Item, Parent


class TestRelationOuterJoinedStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_build(self) -> None:
        strategy = RelationOuterJoinedStrategy(Parent.name)
        self.assert_compile(
            strategy.filter(select(Item.id), Parent.name == "test"),
            "SELECT item.id FROM item LEFT OUTER JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing(self) -> None:
        strategy = RelationOuterJoinedStrategy(Parent.name)
        self.assert_compile(
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

    def test_building_in_filter(self) -> None:
        filter_ = Filter(Parent.name, strategy=RelationOuterJoinedStrategy)
        self.assert_compile(
            filter_.filter(select(Item.id), "test"),
            "SELECT item.id FROM item LEFT OUTER JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )
