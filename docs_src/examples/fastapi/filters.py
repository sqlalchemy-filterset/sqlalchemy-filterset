import uuid

from pydantic import BaseModel
from webapp.models import Category, CategoryType, Product

from sqlalchemy_filterset.filters import (
    Filter,
    InFilter,
    LimitOffsetFilter,
    OrderingField,
    OrderingFilter,
    RangeFilter,
    SearchFilter,
)
from sqlalchemy_filterset.filtersets import FilterSet
from sqlalchemy_filterset.strategies import RelationJoinStrategy


class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    ids = InFilter(Product.id)
    name = SearchFilter(Product.name)
    price = RangeFilter(Product.price)
    is_active = Filter(Product.is_active)
    category_type = Filter(
        Category.type,
        strategy=RelationJoinStrategy(
            Category,
            Product.category_id == Category.id,
        ),
    )
    ordering = OrderingFilter(
        name=OrderingField(Product.name),
        price=OrderingField(Product.price),
    )
    limit_offset = LimitOffsetFilter()


class ProductFilterSchema(BaseModel):
    id: uuid.UUID | None
    ids: list[uuid.UUID] | None
    name: str | None
    price: tuple[float, float] | None
    is_active: bool | None
    category_type: CategoryType | None
    ordering: list[str] | None
    limit_offset: tuple[int | None, int | None] | None

    class Config:
        orm_mode = True
