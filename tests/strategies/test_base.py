from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.strategies import BaseStrategy
from tests.models import Item


class TestBaseStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_filter(self) -> None:
        strategy = BaseStrategy(Item.area)
        self.assert_compile(
            strategy.filter(select(Item.id), Item.area == 1000),
            "SELECT item.id FROM item WHERE item.area = 1000",
            literal_binds=True,
        )
