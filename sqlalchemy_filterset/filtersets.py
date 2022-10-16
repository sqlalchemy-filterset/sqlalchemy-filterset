import abc
import copy
from collections import OrderedDict
from typing import Any, Dict

import sqlalchemy as sa
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from sqlalchemy_filterset.filters import BaseFilter


class FilterSetMetaclass(abc.ABCMeta):
    """Metaclass for creating a FilterSet"""

    def __new__(mcs, name: str, bases: tuple, attrs: Dict[str, Any]) -> "FilterSetMetaclass":
        attrs["declared_filters"] = mcs.get_declared_filters(bases, attrs)
        new_class = super().__new__(mcs, name, bases, attrs)
        return new_class

    @classmethod
    def get_declared_filters(mcs, bases: tuple, attrs: Dict[str, Any]) -> Dict[str, BaseFilter]:
        filters: Dict[str, BaseFilter] = OrderedDict()

        for base in bases:
            if not hasattr(base, "declared_filters"):
                continue
            for filter_name, filter_ in base.declared_filters.items():
                filters[filter_name] = filter_

        for filter_name, filter_ in list(attrs.items()):
            if not isinstance(filter_, BaseFilter):
                continue
            del attrs[filter_name]
            filters[filter_name] = filter_
            if getattr(filter_, "field_name", None) is None:
                filter_.field_name = filter_name

        return filters


class BaseFilterSet(metaclass=FilterSetMetaclass):
    declared_filters: Dict[str, BaseFilter]

    def __init__(self, params: dict, query: Select) -> None:
        """
        :param params: Dictionary of filtration params
        :param query: Base query which uses for building filter query
        """
        self.params = params
        self.__base_query = query
        self.base_filters = self.get_filters()
        self.filters = copy.deepcopy(self.base_filters)
        for filter_ in self.filters.values():
            filter_.parent = self

    def get_base_query(self) -> Select:
        return copy.copy(self.__base_query)

    @classmethod
    def get_filters(cls) -> Dict[str, BaseFilter]:
        """Get Filters of this FilterSet"""
        filters: Dict[str, BaseFilter] = OrderedDict()
        filters.update(cls.declared_filters)
        return filters

    def filter_query(self) -> Select:
        """Build filtration query"""
        query = self.get_base_query()
        for name, value in self.params.items():
            if name not in self.filters:
                continue
            query = self.filters[name].filter(query, value)
        return query

    def count_query(self) -> Select:
        """Build query for calculating the total number of filtration results"""
        query = self.filter_query().limit(None).offset(None)
        cnt = sa.func.count(sa.literal_column("1"))
        if query._distinct and not query._distinct_on:  # type: ignore
            query = sa.select(cnt).select_from(query.order_by(None).subquery())
        elif query._distinct and query._distinct_on:  # type: ignore
            query = sa.select(cnt).select_from(query.subquery())
        else:
            query = query.order_by(None).with_only_columns(cnt, **{"maintain_column_froms": True})
        return query


class FilterSet(BaseFilterSet):
    def __init__(
        self,
        params: dict,
        session: Session,
        query: Select,
    ) -> None:
        """
        :param params: Dictionary of filtration params
        :param session: DB Session
        :param query: Base query which uses for building filter query
        """
        self.session = session
        super().__init__(params, query)

    def filter(self) -> Result:
        """Get filtration results"""
        return self.session.execute(self.filter_query())

    def count(self) -> int:
        """Calculating the total number of filtration results"""
        return self.session.execute(self.count_query()).scalar()  # type: ignore


class AsyncFilterSet(BaseFilterSet):
    def __init__(
        self,
        params: dict,
        session: AsyncSession,
        query: Select,
    ) -> None:
        """
        :param params: Dictionary of filtration params
        :param session: DB Session
        :param query: Base query which uses for building filter query
        """
        self.session = session
        super().__init__(params, query)

    async def filter(self) -> Result:
        """Get filtration results"""
        return await self.session.execute(self.filter_query())

    async def count(self) -> int:
        """Calculating the total number of filtration results"""
        return (await self.session.execute(self.count_query())).scalar()  # type: ignore
