import abc
import copy
from collections import OrderedDict
from typing import Any, Callable, Dict, Mapping, Sequence, Union

import sqlalchemy as sa
from sqlalchemy.engine import Result, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Bundle
from sqlalchemy.sql import ColumnElement, Select

from sqlalchemy_filterset.filters import BaseFilter
from sqlalchemy_filterset.interfaces import IFilterSet


class FilterSetMetaclass(type):
    """Метакласс для создания FilterSet"""

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> "FilterSetMetaclass":
        attrs["declared_filters"] = mcs.get_declared_filters(attrs)
        new_class = super().__new__(mcs, name, bases, attrs)
        return new_class

    @classmethod
    def get_declared_filters(mcs, attrs: dict) -> Dict:
        filters = [
            (filter_name, attrs.pop(filter_name))
            for filter_name, obj in list(attrs.items())
            if isinstance(obj, BaseFilter)
        ]

        for filter_name, f in filters:
            if getattr(f, "field_name", None) is None:
                f.field_name = filter_name

        return OrderedDict(filters)


class BaseFilterSet(IFilterSet):
    """Базовый FilterSet"""

    declared_filters: Dict[str, BaseFilter]

    def __init__(
        self,
        params: dict,
        session: AsyncSession,
        query: Select,
        enable_optimization: bool = True,
    ) -> None:
        """
        :param params: Словарь параметров для фильтрации
        :param session: Сессия базы данных
        :param query: Базовый запрос, на основе которого происходит фильтрация
        :param enable_optimization: Включает оптимизацию запросов при вычислении specs и facets
        """
        self.params = params
        self.__base_query = query
        self.session = session
        self.base_filters = self.get_filters()
        self.filters = copy.deepcopy(self.base_filters)
        self._optimization_enabled = enable_optimization
        for filter_ in self.filters.values():
            filter_.parent = self

    def get_base_query(self) -> Select:
        return copy.copy(self.__base_query)

    @property
    def optimization_enabled(self) -> bool:
        # Оптимизация не совместима с DISTINCT и DISTINCT ON
        if self.get_base_query()._distinct:  # type: ignore
            return False
        return self._optimization_enabled

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

    async def _fetch_common_columns(self, columns: Sequence[Union[Bundle, ColumnElement]]) -> Row:
        query = self.filter_query()
        query = query.with_only_columns(columns).order_by(None)
        return (await self.session.execute(query)).one()

    @staticmethod
    def _parse_common_columns(
        result: Row, field_name_to_parser: Mapping[str, Callable]
    ) -> Dict[str, Any]:
        mapped_result: Dict[str, Any] = {}
        for field_name, parse in field_name_to_parser.items():
            mapped_result[field_name] = parse(getattr(result, field_name))
        return mapped_result


class ABCFilterSetMetaclass(abc.ABCMeta, FilterSetMetaclass):
    pass


class FilterSet(BaseFilterSet, metaclass=ABCFilterSetMetaclass):
    pass
