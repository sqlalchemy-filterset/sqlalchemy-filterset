## FastApi Example

This is an example of an application built using FastAPI, a modern,
fast (high-performance) web framework for building APIs with `Python 3.7+`
based on standard Python type hints. It uses the `SQLAlchemy` library to
handle database operations and the `sqlalchemy_filterset` library for easy
filtering, ordering and pagination of data. The example defines several
data models for a simple e-commerce application, including Product and
Category models, as well as filterset classes and request query models
for handling filtering and ordering of products.
```python
import dataclasses
import enum
import uuid
from typing import Generator, List, Optional, Tuple

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, parse_obj_as
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Numeric, String, create_engine, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

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
from sqlalchemy_filterset.strategies import RelationSubqueryExistsStrategy

Base = declarative_base()


# Models
class CategoryType(enum.Enum):
    foo = "foo"
    bar = "bar"


class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(CategoryType), nullable=False)
    title = Column(String)


class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    price = Column(Numeric)
    is_active = Column(Boolean)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    category: Category = relationship("Category", backref="products")


# Response models
class ProductOut(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    is_active: bool

    class Config:
        orm_mode = True


# Filters
class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    ids = InFilter(Product.id)
    name = SearchFilter(Product.name)
    price = RangeFilter(Product.price)
    is_active = Filter(Product.is_active)
    category_type = Filter(
        Category.type,
        strategy=RelationSubqueryExistsStrategy(Category, Product.category_id == Category.id),
    )
    ordering_filter = OrderingFilter(
        name=OrderingField(Product.name), price=OrderingField(Product.price)
    )
    limit_offset = LimitOffsetFilter()


class ProductFilterSchema(BaseModel):
    id: Optional[uuid.UUID]
    ids: Optional[List[uuid.UUID]]
    name: Optional[str]
    price: Optional[Tuple[float, float]]
    is_active: Optional[bool]
    category_type: Optional[CategoryType]
    ordering_filter: Optional[List[str]]
    limit_offset: Optional[Tuple[Optional[int], Optional[int]]]

    class Config:
        orm_mode = True


engine = create_engine("postgresql://user:password@host/database")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Routes
@dataclasses.dataclass
class ProductQuery:
    id: Optional[uuid.UUID] = Query(None)
    ids: Optional[List[uuid.UUID]] = Query(None)
    exclude_ids: Optional[List[uuid.UUID]] = Query(None)
    is_active: Optional[bool] = Query(None)
    price_range: Optional[Tuple[float, float]] = Query(None)
    category_type: Optional[CategoryType] = Query(None)
    search: Optional[str] = Query(None)
    ordering_filter: Optional[List[str]] = Query(None)
    limit_offset: Optional[Tuple[Optional[int], Optional[int]]] = Query(None)


@app.get("/products/")
def list_products(
    filters: ProductQuery = Depends(),
    db: Session = Depends(get_db),
) -> List[ProductOut]:
    filter_set = ProductFilterSet(db, select(Product))
    filter_params = parse_obj_as(ProductFilterSchema, filters)
    filtered_products = filter_set.filter(filter_params.dict(exclude_none=True))
    return parse_obj_as(List[ProductOut], filtered_products)
```
