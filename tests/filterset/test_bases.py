import typing
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filterset.constants import EMPTY_VALUES
from sqlalchemy_filterset.filters import Filter, InFilter
from sqlalchemy_filterset.filtersets import AsyncFilterSet
from tests.filterset.conftest import ItemFactory
from tests.models import GrandGrandParent, GrandParent, Item, Parent


class FilterSetClass(AsyncFilterSet):
    id = Filter(Item.id)
    ids = InFilter(Item.id)


@pytest.mark.parametrize("empty_value", EMPTY_VALUES)
@pytest.mark.parametrize("field", ["id", "ids"])
async def test_empty_values(empty_value: Any, field: str, db_session: AsyncSession) -> None:
    three_items: typing.List[Item] = await ItemFactory.create_batch(3)
    base_query = select(Item).join(Parent).join(GrandParent).join(GrandGrandParent)
    filter_set = FilterSetClass(db_session, base_query)
    result = await db_session.execute(filter_set.filter_query({f"{field}": empty_value}))
    actual = result.scalars().all()
    assert set(three_items) == set(actual)


async def test_wrong_field(db_session: AsyncSession) -> None:
    three_items: typing.List[Item] = await ItemFactory.create_batch(3)
    base_query = select(Item).join(Parent).join(GrandParent).join(GrandGrandParent)
    filter_set = FilterSetClass(db_session, base_query)
    result = await db_session.execute(filter_set.filter_query({"test": "test"}))
    actual = result.scalars().all()
    assert set(three_items) == set(actual)
