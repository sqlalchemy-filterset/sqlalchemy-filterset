import abc
import copy
from collections import OrderedDict
from typing import Any, Dict, Generic, Sequence, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from sqlalchemy_filterset.filters import BaseFilter
from sqlalchemy_filterset.strategies import ApplicableStrategy


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


Model = TypeVar("Model")


class BaseFilterSet(Generic[Model], metaclass=FilterSetMetaclass):
    declared_filters: Dict[str, BaseFilter]

    def __init__(self, query: Select) -> None:
        """
        :param query: Base query which uses for building filter query
        """
        self.__base_query = query
        self.filters = self.get_filters()
        for filter_ in self.filters.values():
            filter_.filter_set = self

    def get_base_query(self) -> Select:
        return copy.copy(self.__base_query)

    @classmethod
    def get_filters(cls) -> Dict[str, BaseFilter]:
        """Get Filters of this FilterSet"""
        filters: Dict[str, BaseFilter] = OrderedDict()
        filters.update(cls.declared_filters)
        return filters

    def filter_query(self, params: Dict) -> Select:
        """Build filtration query"""
        query = self.get_base_query()
        applied_strategies = []
        for name, value in params.items():
            if name not in self.filters:
                continue
            filter = self.filters[name]
            if hasattr(filter, "strategy") and isinstance(filter.strategy, ApplicableStrategy):
                for strategy in applied_strategies:
                    if strategy == filter.strategy:
                        break
                else:
                    query = filter.strategy.apply(query)
                    applied_strategies.append(filter.strategy)
            query = filter.filter(query, value, params)
        return query

    def count_query(self, params: Dict) -> Select:
        """Build query for calculating the total number of filtration results"""
        query = self.filter_query(params).limit(None).offset(None)
        cnt = sa.func.count(sa.literal_column("1"))
        if query._distinct and not query._distinct_on:
            query = sa.select(cnt).select_from(query.order_by(None).subquery())
        elif query._distinct and query._distinct_on:
            query = sa.select(cnt).select_from(query.subquery())
        else:
            query = query.order_by(None).with_only_columns(cnt, maintain_column_froms=True)
        return query


class FilterSet(BaseFilterSet[Model]):
    def __init__(
        self,
        session: Session,
        query: Select,
    ) -> None:
        """
        :param session: DB Session
        :param query: Base query which uses for building filter query
        """
        self.session = session
        super().__init__(query)

    def filter(self, params: Dict) -> Sequence[Model]:
        """Get filtration results"""
        return self.session.execute(self.filter_query(params)).unique().scalars().all()

    def count(self, params: Dict) -> int:
        """Calculating the total number of filtration results"""
        return self.session.execute(self.count_query(params)).scalar()  # type: ignore


class AsyncFilterSet(BaseFilterSet[Model]):
    def __init__(
        self,
        session: AsyncSession,
        query: Select,
    ) -> None:
        """
        :param session: DB Session
        :param query: Base query which uses for building filter query
        """
        self.session = session
        super().__init__(query)

    async def filter(self, params: Dict) -> Sequence[Model]:
        """Get filtration results"""
        return (await self.session.execute(self.filter_query(params))).unique().scalars().all()

    async def count(self, params: Dict) -> int:
        """Calculating the total number of filtration results"""
        return (await self.session.execute(self.count_query(params))).scalar()  # type: ignore
