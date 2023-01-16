from typing import List

from fastapi import Depends
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.orm import Session
from webapp.applications import app, get_db
from webapp.filters import ProductFilterSchema, ProductFilterSet
from webapp.models import Product
from webapp.queries import ProductQuery
from webapp.schemas import ProductOut


@app.get("/products/")
def list_products(
    filters: ProductQuery = Depends(),
    db: Session = Depends(get_db),
) -> List[ProductOut]:
    filter_set = ProductFilterSet(db, select(Product))
    filter_params = parse_obj_as(ProductFilterSchema, filters)
    filtered_products = filter_set.filter(filter_params.dict(exclude_none=True))
    return parse_obj_as(List[ProductOut], filtered_products)
