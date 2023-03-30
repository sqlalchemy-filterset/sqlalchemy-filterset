from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import Mapped, registry

mapper_registry = registry()


@dataclass
class Person:
    id: Mapped[int] = field(init=False)
    name: Mapped[str]


person = Table(
    "person",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
)

mapper_registry.map_imperatively(Person, person)
