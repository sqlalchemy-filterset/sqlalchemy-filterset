from sqlalchemy import select
from sqlalchemy.testing import AssertsCompiledSQL

from sqlalchemy_filterset.filters import Filter
from sqlalchemy_filterset.strategies import BaseStrategy
from tests.models import Item


class TestBaseStrategy(AssertsCompiledSQL):
    __dialect__: str = "default"

    def test_build(self) -> None:
        strategy = BaseStrategy(Item.area)
        self.assert_compile(
            strategy.filter(select(Item.id), Item.area == 1000),
            "SELECT item.id FROM item WHERE item.area = 1000",
            literal_binds=True,
        )

    def test_building_in_filter(self) -> None:
        filter_ = Filter(Item.area, strategy=BaseStrategy)
        self.assert_compile(
            filter_.filter(select(Item.id), 1000),
            "SELECT item.id FROM item WHERE item.area = 1000",
            literal_binds=True,
        )
