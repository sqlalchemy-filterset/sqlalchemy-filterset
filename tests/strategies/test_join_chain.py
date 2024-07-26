from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import JoinChainStrategy, RelationJoinStrategy
from tests.models.base import Item, ItemLink, ItemToItemLink


class TestJoinChainStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = JoinChainStrategy(
            RelationJoinStrategy(
                ItemToItemLink,
                Item.id == ItemToItemLink.right_id,
            ),
            RelationJoinStrategy(
                ItemLink,
                ItemLink.id == ItemToItemLink.left_id,
            ),
        )
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id), ItemLink.name == "test"),
            "SELECT item.id FROM item "
            "JOIN item_to_item_link ON item.id = item_to_item_link.right_id "
            "JOIN item_link ON item_link.id = item_to_item_link.left_id "
            "WHERE item_link.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing_association_table(self) -> None:
        strategy = JoinChainStrategy(
            RelationJoinStrategy(
                ItemToItemLink,
                Item.id == ItemToItemLink.right_id,
            ),
            RelationJoinStrategy(
                ItemLink,
                ItemLink.id == ItemToItemLink.left_id,
            ),
        )
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id).join(ItemToItemLink), ItemLink.name == "test"),
            "SELECT item.id FROM item "
            "JOIN item_to_item_link ON item.id = item_to_item_link.right_id "
            "JOIN item_link ON item_link.id = item_to_item_link.left_id "
            "WHERE item_link.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_preventing(self) -> None:
        strategy = JoinChainStrategy(
            RelationJoinStrategy(
                ItemToItemLink,
                Item.id == ItemToItemLink.right_id,
            ),
            RelationJoinStrategy(
                ItemLink,
                ItemLink.id == ItemToItemLink.left_id,
            ),
        )
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id)
                .join(ItemToItemLink, Item.id == ItemToItemLink.right_id)
                .join(
                    ItemLink,
                    ItemLink.id == ItemToItemLink.left_id,
                ),
                ItemLink.name == "test",
            ),
            "SELECT item.id FROM item "
            "JOIN item_to_item_link ON item.id = item_to_item_link.right_id "
            "JOIN item_link ON item_link.id = item_to_item_link.left_id "
            "WHERE item_link.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_with_different_onclause_association_table(self) -> None:
        strategy = JoinChainStrategy(
            RelationJoinStrategy(
                ItemToItemLink,
                Item.id == ItemToItemLink.right_id,
            ),
            RelationJoinStrategy(
                ItemLink,
                ItemLink.id == ItemToItemLink.left_id,
            ),
        )
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id).join(ItemToItemLink, Item.parent_id == ItemToItemLink.right_id),
                ItemLink.name == "test",
            ),
            "SELECT item.id FROM item "
            "JOIN item_to_item_link ON item.parent_id = item_to_item_link.right_id "
            "JOIN item_to_item_link ON item.id = item_to_item_link.right_id "
            "JOIN item_link ON item_link.id = item_to_item_link.left_id "
            "WHERE item_link.name = 'test'",
            literal_binds=True,
        )

    def test_double_join_with_different_onclause(self) -> None:
        strategy = JoinChainStrategy(
            RelationJoinStrategy(
                ItemToItemLink,
                Item.id == ItemToItemLink.right_id,
            ),
            RelationJoinStrategy(
                ItemLink,
                ItemLink.id == ItemToItemLink.left_id,
            ),
        )
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(
                select(Item.id)
                .join(ItemToItemLink, Item.id == ItemToItemLink.right_id)
                .join(
                    ItemLink,
                    ItemLink.id == ItemToItemLink.right_id,
                ),
                ItemLink.name == "test",
            ),
            "SELECT item.id FROM item "
            "JOIN item_to_item_link ON item.id = item_to_item_link.right_id "
            "JOIN item_link ON item_link.id = item_to_item_link.right_id "
            "JOIN item_link ON item_link.id = item_to_item_link.left_id "
            "WHERE item_link.name = 'test'",
            literal_binds=True,
        )
