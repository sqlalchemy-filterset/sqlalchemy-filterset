import uuid
from typing import List, Optional, Tuple

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
from sqlalchemy_filterset.strategies import RelationOuterJoinStrategy


class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    ids = InFilter(Product.id)
    name = SearchFilter(Product.name)
    price = RangeFilter(Product.price)
    is_active = Filter(Product.is_active)
    category_type = Filter(
        Category.type,
        strategy=RelationOuterJoinStrategy(Category, Product.category_id == Category.id),
    )
    ordering = OrderingFilter(name=OrderingField(Product.name), price=OrderingField(Product.price))
    limit_offset = LimitOffsetFilter()


class ProductFilterSchema(BaseModel):
    id: Optional[uuid.UUID]
    ids: Optional[List[uuid.UUID]]
    name: Optional[str]
    price: Optional[Tuple[float, float]]
    is_active: Optional[bool]
    category_type: Optional[CategoryType]
    ordering: Optional[List[str]]
    limit_offset: Optional[Tuple[Optional[int], Optional[int]]]

    class Config:
        orm_mode = True
