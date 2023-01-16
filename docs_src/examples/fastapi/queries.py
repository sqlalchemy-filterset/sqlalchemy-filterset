import dataclasses
import uuid

from fastapi import Query
from myapp.models import CategoryType


@dataclasses.dataclass
class ProductQuery:
    id: uuid.UUID | None = Query(None)
    ids: list[uuid.UUID] | None = Query(None)
    name: str | None = Query(None)
    price_min: int | None = Query(None)
    price_max: int | None = Query(None)
    is_active: bool | None = Query(None)
    category_type: CategoryType | None = Query(None)
    ordering: list[str] | None = Query(None)
    limit: int | None = Query(None)
    offset: int | None = Query(None)

    @property
    def limit_offset(self) -> tuple[int | None, int | None] | None:
        if self.limit or self.offset:
            return self.limit, self.offset
        return None

    @property
    def price(self) -> tuple[float, float] | None:
        if self.price_min and self.price_max:
            return self.price_min, self.price_max
        return None
