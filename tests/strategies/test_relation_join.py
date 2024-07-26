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
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id).join(Parent), Parent.name == "test"),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id).join(Parent, onclause=Parent.id == Item.parent_id),
                Parent.name == "test",
            ),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id WHERE parent.name = 'test'",
            literal_binds=True,
        )

        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id)
                .join(Parent, onclause=Parent.id == Item.parent_id)
                .join(GrandParent, onclause=GrandParent.id == Parent.parent_id),
                Parent.name == "test",
            ),
            "SELECT item.id FROM item "
            "JOIN parent ON parent.id = item.parent_id "
            "JOIN grand_parent ON grand_parent.id = parent.parent_id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )

        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                strategy.filter(select(Item.id), Parent.name == "test"), Parent.name != "test1"
            ),
            "SELECT item.id FROM item JOIN parent "
            "ON parent.id = item.parent_id "
            "WHERE parent.name = 'test' AND parent.name != 'test1'",
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

    def test_double_join_with_different_join_types(self) -> None:
        strategy = RelationJoinStrategy(Parent, onclause=Parent.id == Item.parent_id)

        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id).outerjoin(Parent, onclause=Parent.id == Item.parent_id),
                Parent.name == "test",
            ),
            "SELECT item.id FROM item "
            "LEFT OUTER JOIN parent ON parent.id = item.parent_id "
            "JOIN parent ON parent.id = item.parent_id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )

        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id).join(Parent, onclause=Parent.id == Item.parent_id, full=True),
                Parent.name == "test",
            ),
            "SELECT item.id FROM item "
            "FULL OUTER JOIN parent ON parent.id = item.parent_id "
            "JOIN parent ON parent.id = item.parent_id "
            "WHERE parent.name = 'test'",
            literal_binds=True,
        )
