import operator as op
from typing import Any, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from sqlalchemy_filterset.filters import Filter as FFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet, FilterSetMetaclass
from sqlalchemy_filterset.strategies import BaseStrategy
from sqlalchemy_filterset.types import LookupExpr, ModelAttribute
from tests.models.base import Item


def Filter(
    field: ModelAttribute,
    *,
    lookup_expr: LookupExpr = op.eq,
    strategy: Optional[BaseStrategy] = None,
) -> Any:
    return FFilter(field, lookup_expr=lookup_expr, strategy=strategy)


class ItemFilterSet(BaseFilterSet[Item]):
    id: str = Filter(Item.id)


class FilterSetToFilterSchemaMetaclass(ModelMetaclass, FilterSetMetaclass):
    def __new__(cls, name, bases, attrs):
        annotations = attrs.get("__annotations__", {})
        for base in bases:
            if not issubclass(base, BaseFilterSet):
                continue
            annotations = {**base.__dict__.get("__annotations__", {}), **annotations}
        attrs["__annotations__"] = annotations
        return super().__new__(cls, name, bases, attrs)


class FilterSetToFilterSchema(BaseModel, metaclass=FilterSetToFilterSchemaMetaclass):
    pass


class ItemFilterSchema(FilterSetToFilterSchema, ItemFilterSet):
    pass


class TestFilterSchema:
    def test_direct(self) -> None:
        filter_schema = ItemFilterSchema(id="test")
        assert filter_schema.id == "test"
        assert filter_schema.dict() == {"id": "test"}

    def test_parse(self) -> None:
        filter_schema = ItemFilterSchema.parse_raw('{"id":"test"}')
        assert filter_schema.id == "test"
        assert filter_schema.dict() == {"id": "test"}
