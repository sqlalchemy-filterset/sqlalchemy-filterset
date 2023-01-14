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
    price: Optional[Tuple[float, float]] = Query(None)
    is_active: Optional[bool] = Query(None)
    category_type: Optional[CategoryType] = Query(None)
    ordering: Optional[List[str]] = Query(None)
    limit_offset: Optional[Tuple[Optional[int], Optional[int]]] = Query(None)
