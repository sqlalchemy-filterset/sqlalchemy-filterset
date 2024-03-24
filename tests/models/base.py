import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

import sqlalchemy as sa
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from tests.database.base import Base


class ItemType(Enum):
    foo = "foo"
    bar = "bar"


class GrandGrandParent(Base):
    id: Column[uuid.UUID] = Column(UUID, primary_key=True, default=uuid.uuid4)
    name: Column[str] = Column(sa.String, nullable=True)


class GrandParent(Base):
    id: Column[uuid.UUID] = Column(UUID, primary_key=True, default=uuid.uuid4)
    parent_id: Column[uuid.UUID] = Column(
        UUID,
        sa.ForeignKey("grand_grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: Mapped[GrandGrandParent] = relationship("GrandGrandParent", backref="childs")
    name: Column[str] = Column(sa.String, nullable=True)


class Parent(Base):
    id: Column[uuid.UUID] = Column(UUID, primary_key=True, default=uuid.uuid4)
    date: Column[datetime] = Column(DateTime(), nullable=False, server_default=sa.func.now())
    parent_id: Column[uuid.UUID] = Column(
        UUID,
        sa.ForeignKey("grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: Mapped[GrandParent] = relationship("GrandParent", backref="childs")
    name: Column[str] = Column(sa.String, nullable=True)


class Item(Base):
    id: Column[uuid.UUID] = Column(UUID, primary_key=True, default=uuid.uuid4)
    name: Column[str] = Column(sa.String, nullable=True)
    description: Column[str] = Column(sa.Text, nullable=True)
    date: Column[datetime] = Column(DateTime(), nullable=False, server_default=sa.func.now())
    area: Column[Decimal] = Column(sa.Numeric(precision=8, scale=3), nullable=True)
    is_active: Column[bool] = Column(sa.Boolean, server_default="t", nullable=False)
    title: Column[str] = Column(sa.String, nullable=True)
    type: Column[ItemType] = Column(AlchemyEnum(ItemType), nullable=True)
    parent_id: Column[uuid.UUID] = Column(
        UUID, sa.ForeignKey("parent.id", ondelete="CASCADE"), nullable=False
    )
    parent: Mapped[Parent] = relationship("Parent", backref="childs")
