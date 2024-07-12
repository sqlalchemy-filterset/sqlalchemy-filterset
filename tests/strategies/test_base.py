from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import BaseStrategy
from tests.models.base import Item


class TestBaseStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_strategy_uniq(self) -> None:
        assert BaseStrategy() != BaseStrategy()

    def test_filter(self) -> None:
        strategy = BaseStrategy()
        self.assert_compile(  # type: ignore[no-untyped-call]
            strategy.filter(select(Item.id), Item.area == 1000),
            "SELECT item.id FROM item WHERE item.area = 1000",
            literal_binds=True,
        )
