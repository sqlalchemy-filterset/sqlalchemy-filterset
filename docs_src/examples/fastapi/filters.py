import uuid

from pydantic import BaseModel
from webapp.models import Category, CategoryType, Product, Tag, TagToProduct

from sqlalchemy_filterset import (
    Filter,
    FilterSet,
    InFilter,
    JoinStrategy,
    LimitOffsetFilter,
    MultiJoinStrategy,
    OrderingField,
    OrderingFilter,
    RangeFilter,
    SearchFilter,
)


class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    ids = InFilter(Product.id)
    name = SearchFilter(Product.name)
    price = RangeFilter(Product.price)
    is_active = Filter(Product.is_active)
    category_type = Filter(
        Category.type,
        strategy=JoinStrategy(
            Category,
            Product.category_id == Category.id,
        ),
    )
    tag_title = Filter(
        Tag.title,
        strategy=MultiJoinStrategy(
            JoinStrategy(TagToProduct, onclause=Product.id == TagToProduct.right_id),
            JoinStrategy(Tag, onclause=Tag.id == TagToProduct.left_id),
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
    tag_title: str | None
    ordering: list[str] | None
    limit_offset: tuple[int | None, int | None] | None

    class Config:
        orm_mode = True
