import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

import sqlalchemy as sa
from sqlalchemy import DateTime
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tests.database.base import Base


class ItemType(Enum):
    foo = "foo"
    bar = "bar"


class GrandGrandParent(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String, nullable=True)


class GrandParent(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        sa.ForeignKey("grand_grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: GrandGrandParent = relationship("GrandGrandParent", backref="childs")
    name: Mapped[str] = mapped_column(sa.String, nullable=True)


class Parent(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=sa.func.now())
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        sa.ForeignKey("grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: GrandParent = relationship("GrandParent", backref="childs")
    name: Mapped[str] = mapped_column(sa.String, nullable=True)


class Item(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String, nullable=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=sa.func.now())
    area: Mapped[Decimal] = mapped_column(sa.Numeric(precision=8, scale=3), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, server_default="t", nullable=False)
    title: Mapped[str] = mapped_column(sa.String, nullable=True)
    type: Mapped[ItemType] = mapped_column(AlchemyEnum(ItemType), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID, sa.ForeignKey("parent.id", ondelete="CASCADE"), nullable=False
    )
    parent: Parent = relationship("Parent", backref="childs")
