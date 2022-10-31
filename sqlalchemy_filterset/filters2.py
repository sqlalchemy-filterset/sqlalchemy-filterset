import abc
import operator as op
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Optional

from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import Select
from sqlalchemy.sql import operators as sa_op

from sqlalchemy_filterset.constants import EMPTY_VALUES

if TYPE_CHECKING:
    from sqlalchemy_filterset.filtersets import BaseFilterSet  # pragma: no cover


LOOKUP_EXPR = (
    op.eq,  # <a> = <b>
    op.ne,  # <a> != <b>
    op.le,  # <a> <= <b>
    op.lt,  # <a> < <b>
    op.ge,  # <a> >= <b>
    op.gt,  # <a> > <b>
    sa_op.in_op,  # <a> IN <b>
    sa_op.not_in_op,  # <a> NOT IN <b>
    sa_op.is_,  # <a> IS <b>
    sa_op.is_not,  # <a> IS NOT <b>
    sa_op.like_op,  # <a> LIKE <b>
    sa_op.not_like_op,  # <a> NOT LIKE <b>
    sa_op.ilike_op,  # LOWER(<a>) LIKE <b>
    sa_op.not_ilike_op,  # LOWER(<a>) NOT LIKE <b>
    sa_op.startswith_op,  # <a> LIKE <b> || '%'
    sa_op.not_startswith_op,  # <a> NOT LIKE <b> || '%'
    sa_op.endswith_op,  # <a> LIKE '%' || <b>
    sa_op.not_endswith_op,  # <a> NOT LIKE '%' || <b>
    sa_op.contains_op,  # <a> LIKE '%' || <b> || '%'
    sa_op.not_contains_op,  # <a> NOT LIKE '%' || <b> || '%'
    # match_op
    # not_match_op
    # regexp_match_op
    # not_regexp_match_op
    # regexp_replace_op
    # sa_op.any_op,
    # sa_op.all_op,
    # sa_op.between_op,
    # sa_op.not_between_op
)

# todo: between_op
# todo: regexp
# todo: any_op
# todo: all_op
# todo: remove nullable=True
# todo: search filter % ilike %
# todo: range filter
# todo: boolean filter


class BaseFilter:
    field_name: Optional[str] = None
    "Name of Filter in FilterSet. Set by FilterSet after creation."

    def __init__(self) -> None:
        self.parent: Optional["BaseFilterSet"] = None

    @abc.abstractmethod
    def filter(self, query: Select, value: Any) -> Select:
        """Implementation of query build for this Filter"""
        ...  # pragma: no cover


class Filter(BaseFilter):
    """Base Filter by filed"""

    def __init__(
        self,
        field: QueryableAttribute,
        *,
        lookup_expr: Callable = op.eq,
        nullable: bool = False,
    ) -> None:
        """
        :param field: Filed of Model for filtration
        :param nullable: Allow empty values in filtration process
        """
        super().__init__()
        expr: Callable = lookup_expr.func if isinstance(lookup_expr, partial) else lookup_expr
        if expr not in LOOKUP_EXPR:
            raise Exception(f"Incorrect lookup_expr {expr}")

        self.field = field
        self.lookup_expr = lookup_expr
        self.nullable = nullable

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query
        return query.where(self.lookup_expr(self.field, value))
