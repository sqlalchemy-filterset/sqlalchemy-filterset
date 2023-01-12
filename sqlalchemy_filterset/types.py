from typing import Any, Callable, Union

from sqlalchemy import Table
from sqlalchemy.orm import InstrumentedAttribute, QueryableAttribute
from typing_extensions import Protocol

ModelAttribute = Union[QueryableAttribute, InstrumentedAttribute, Any]
LookupExpr = Callable[[Any, Any], Any]


class Model(Protocol):
    __table__: Table
