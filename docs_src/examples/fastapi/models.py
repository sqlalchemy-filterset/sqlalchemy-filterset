import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class CategoryType(enum.Enum):
    foo = "foo"
    bar = "bar"


class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(CategoryType), nullable=False)
    title = Column(String)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)


class TagToProduct(Base):
    __tablename__ = "tag_to_product"
    left_id = Column(
        UUID,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    )
    right_id = Column(
        UUID,
        ForeignKey("product.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    price = Column(Numeric)
    is_active = Column(Boolean)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
    )
    category: Category = relationship("Category", backref="products")
