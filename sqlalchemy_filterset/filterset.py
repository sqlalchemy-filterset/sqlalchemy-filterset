import abc
import copy
from collections import OrderedDict
from typing import Dict

import sqlalchemy as sa
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from sqlalchemy_filterset.filters import BaseFilter
from sqlalchemy_filterset.interfaces import IFilterSet


class FilterSetMetaclass(abc.ABCMeta):
    """Метакласс для создания FilterSet"""

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> "FilterSetMetaclass":
        attrs["declared_filters"] = mcs.get_declared_filters(attrs)
        new_class = super().__new__(mcs, name, bases, attrs)
        return new_class

    @classmethod
    def get_declared_filters(mcs, attrs: dict) -> Dict[str, BaseFilter]:
        filters: Dict[str, BaseFilter] = OrderedDict()
        for filter_name, filter_ in list(attrs.items()):
            if not isinstance(filter_, BaseFilter):
                continue
            del attrs[filter_name]
            filters[filter_name] = filter_
            if getattr(filter_, "field_name", None) is None:
                filter_.field_name = filter_name

        return filters


class BaseFilterSet(IFilterSet):
    """Базовый FilterSet"""

    declared_filters: Dict[str, BaseFilter]

    def __init__(
        self,
        params: dict,
        session: AsyncSession,
        query: Select,
    ) -> None:
        """
        :param params: Словарь параметров для фильтрации
        :param session: Сессия базы данных
        :param query: Базовый запрос, на основе которого происходит фильтрация
        """
        self.params = params
        self.__base_query = query
        self.session = session
        self.base_filters = self.get_filters()
        self.filters = copy.deepcopy(self.base_filters)
        for filter_ in self.filters.values():
            filter_.parent = self

    def get_base_query(self) -> Select:
        return copy.copy(self.__base_query)

    @classmethod
    def get_filters(cls) -> Dict[str, BaseFilter]:
        """Получение фильтров для данного FilterSet"""
        filters: Dict[str, BaseFilter] = OrderedDict()
        filters.update(cls.declared_filters)
        return filters

    def filter_query(self) -> Select:
        """Построение запроса для фильтрации"""
        query = self.get_base_query()
        for name, value in self.params.items():
            if name not in self.filters:
                continue
            query = self.filters[name].filter(query, value)
        return query

    async def filter(self) -> Result:
        return await self.session.execute(self.filter_query())

    async def count(
        self, attr_name: str = "id", distinct: bool = False, exclude_pagination: bool = True
    ) -> int:
        """Получения кол-ва результатов для данного FilterSet"""
        base_query = self.filter_query().order_by(None)
        if exclude_pagination:
            base_query = base_query.limit(None).offset(None)
        subquery = base_query.alias("s")
        attr = getattr(subquery.c, attr_name)
        if distinct:
            attr = sa.distinct(attr)
        query = sa.select([sa.func.count(attr)])
        return (await self.session.execute(query)).scalar()  # type: ignore


class FilterSet(BaseFilterSet, metaclass=FilterSetMetaclass):
    pass
