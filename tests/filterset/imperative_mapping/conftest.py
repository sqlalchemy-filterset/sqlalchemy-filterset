from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import registry

mapper_registry = registry()


@dataclass
class Person:
    id: int = field(init=False)
    name: str


person_table = Table(
    "person",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
)

mapper_registry.map_imperatively(Person, person_table)
