import datetime
import uuid
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tests.database.base import Base


class RealtyObject(Base):
    __table_args__ = (
        UniqueConstraint(
            "number",
            "name",
            name="ix_unique_number_name",
        ),
    )

    id: uuid.UUID = sa.Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True)
    number: int = sa.Column(sa.Integer(), server_default=sa.text("0"), nullable=False)
    name: str | None = sa.Column(sa.String(), nullable=True)
    changed: datetime.datetime = sa.Column(
        sa.DateTime(),
        nullable=False,
        server_default=sa.func.now(),
    )
    is_active: bool = sa.Column(sa.Boolean, nullable=False)


class GrandGrandParent(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name: str = sa.Column(sa.String, nullable=True)


class GrandParent(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    parent_id: uuid.UUID = sa.Column(
        UUID(as_uuid=False),
        sa.ForeignKey("grand_grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: GrandGrandParent = relationship("GrandGrandParent", backref="childs")
    name: str = sa.Column(sa.String, nullable=True)


class Parent(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    date: datetime.datetime = sa.Column(
        sa.DateTime(timezone=False),
        nullable=False,
        server_default=sa.func.now(),
    )
    parent_id: uuid.UUID = sa.Column(
        UUID(as_uuid=False),
        sa.ForeignKey("grand_parent.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent: GrandParent = relationship("GrandParent", backref="childs")
    name: str = sa.Column(sa.String, nullable=True)


class ItemForFilters(Base):
    id: uuid.UUID = sa.Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    date: datetime.datetime = sa.Column(
        sa.DateTime(timezone=False), nullable=False, server_default=sa.func.now()
    )
    area: Decimal = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True)
    is_active: bool = sa.Column(sa.Boolean, server_default="t", nullable=False)
    title: str = sa.Column(sa.String, nullable=True)
    parent_id: uuid.UUID = sa.Column(
        UUID(as_uuid=False), sa.ForeignKey("parent.id", ondelete="CASCADE"), nullable=False
    )
    parent: Parent = relationship("Parent", backref="childs")


class Item(Base):
    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    parent_id: int | None = sa.Column(sa.Integer, nullable=True)
    order: int = sa.Column(sa.Integer(), server_default=sa.text("0"), nullable=False)
