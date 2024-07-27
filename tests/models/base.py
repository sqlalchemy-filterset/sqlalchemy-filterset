import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from tests.database.base import Base


class ItemType(Enum):
    foo = "foo"
    bar = "bar"


class GrandGrandParent(Base):
    id: sa.Column[uuid.UUID] = sa.Column(UUID, primary_key=True, default=uuid.uuid4)
    name: sa.Column[str] = sa.Column(sa.String, nullable=True)


class GrandParent(Base):
    id: sa.Column[uuid.UUID] = sa.Column(UUID, primary_key=True, default=uuid.uuid4)
    parent_id: sa.Column[uuid.UUID] = sa.Column(
        UUID,
        sa.ForeignKey("grand_grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: Mapped[GrandGrandParent] = relationship("GrandGrandParent", backref="childs")
    name: sa.Column[str] = sa.Column(sa.String, nullable=True)


class Parent(Base):
    id: sa.Column[uuid.UUID] = sa.Column(UUID, primary_key=True, default=uuid.uuid4)
    date: sa.Column[datetime] = sa.Column(
        sa.DateTime(), nullable=False, server_default=sa.func.now()
    )
    parent_id: sa.Column[uuid.UUID] = sa.Column(
        UUID,
        sa.ForeignKey("grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: Mapped[GrandParent] = relationship("GrandParent", backref="childs")
    name: sa.Column[str] = sa.Column(sa.String, nullable=True)


class ItemToItemLink(Base):
    left_id: sa.Column[uuid.UUID] = sa.Column(
        UUID,
        sa.ForeignKey("item_link.id", ondelete="CASCADE"),
        primary_key=True,
    )
    right_id: sa.Column[uuid.UUID] = sa.Column(
        UUID,
        sa.ForeignKey("item.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ItemLink(Base):
    id: sa.Column[uuid.UUID] = sa.Column(UUID, primary_key=True, default=uuid.uuid4)
    name: sa.Column[str] = sa.Column(sa.String, nullable=True)


class Item(Base):
    id: sa.Column[uuid.UUID] = sa.Column(UUID, primary_key=True, default=uuid.uuid4)
    name: sa.Column[str] = sa.Column(sa.String, nullable=True)
    description: sa.Column[str] = sa.Column(sa.Text, nullable=True)
    date: sa.Column[datetime] = sa.Column(
        sa.DateTime(), nullable=False, server_default=sa.func.now()
    )
    area: sa.Column[Decimal] = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True)
    is_active: sa.Column[bool] = sa.Column(sa.Boolean, server_default="t", nullable=False)
    title: sa.Column[str] = sa.Column(sa.String, nullable=True)
    type: sa.Column[ItemType] = sa.Column(sa.Enum(ItemType), nullable=True)
    parent_id: sa.Column[uuid.UUID] = sa.Column(
        UUID, sa.ForeignKey("parent.id", ondelete="CASCADE"), nullable=False
    )
    parent: Mapped[Parent] = relationship("Parent", backref="childs")

    links: Mapped[List["ItemLink"]] = relationship(secondary="item_to_item_link")
