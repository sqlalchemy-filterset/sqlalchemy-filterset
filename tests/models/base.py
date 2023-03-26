import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

import sqlalchemy as sa
from sqlalchemy import DateTime
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tests.database.base import Base


class ItemType(Enum):
    foo = "foo"
    bar = "bar"


class TestDateTimeType(TypeDecorator):
    impl = DateTime

    def process_literal_param(self, value: Any, dialect: Any) -> str:
        return value.strftime("'%Y-%m-%d %H:%M:%S'")


class GrandGrandParent(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = sa.Column(sa.String, nullable=True)


class GrandParent(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: uuid.UUID = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("grand_grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: GrandGrandParent = relationship("GrandGrandParent", backref="childs")
    name: str = sa.Column(sa.String, nullable=True)


class Parent(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: datetime = sa.Column(TestDateTimeType(), nullable=False, server_default=sa.func.now())
    parent_id: uuid.UUID = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: GrandParent = relationship("GrandParent", backref="childs")
    name: str = sa.Column(sa.String, nullable=True)


class Item(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = sa.Column(sa.String, nullable=True)
    description: str = sa.Column(sa.Text, nullable=True)
    date: datetime = sa.Column(TestDateTimeType(), nullable=False, server_default=sa.func.now())
    area: Decimal = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True)
    is_active: bool = sa.Column(sa.Boolean, server_default="t", nullable=False)
    title: str = sa.Column(sa.String, nullable=True)
    type: ItemType = sa.Column(AlchemyEnum(ItemType), nullable=True)
    parent_id: uuid.UUID = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("parent.id", ondelete="CASCADE"), nullable=False
    )
    parent: Parent = relationship("Parent", backref="childs")
