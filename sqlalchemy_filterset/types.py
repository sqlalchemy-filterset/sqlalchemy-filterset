from typing import Any, Callable

from sqlalchemy import Table
from typing_extensions import Protocol

LookupExpr = Callable[[Any, Any], Any]


class Model(Protocol):
    __table__: Table
