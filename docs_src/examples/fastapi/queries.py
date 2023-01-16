import dataclasses
import uuid
from typing import List, Optional, Tuple

from fastapi import Query
from myapp.models import CategoryType


@dataclasses.dataclass
class ProductQuery:
    id: Optional[uuid.UUID] = Query(None)
    ids: Optional[List[uuid.UUID]] = Query(None)
    name: Optional[str] = Query(None)
    price_min: Optional[int] = Query(None)
    price_max: Optional[int] = Query(None)
    is_active: Optional[bool] = Query(None)
    category_type: Optional[CategoryType] = Query(None)
    ordering: Optional[List[str]] = Query(None)
    limit: Optional[int] = Query(None)
    offset: Optional[int] = Query(None)

    @property
    def limit_offset(self) -> Optional[Tuple[Optional[int], Optional[int]]]:
        if self.limit or self.offset:
            return self.limit, self.offset
        return None

    @property
    def price(self) -> Optional[Tuple[float, float]]:
        if self.price_min and self.price_max:
            return self.price_min, self.price_max
        return None
