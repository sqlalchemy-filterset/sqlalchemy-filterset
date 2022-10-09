import abc
from typing import Any, Optional, Sequence

from sqlalchemy.sql import Select

from sqlalchemy_filterset.constants import EMPTY_VALUES
from sqlalchemy_filterset.interfaces import IBaseFilter


class BaseFilter(IBaseFilter):
    """Абстрактный класс фильтра"""

    field_name: Optional[str] = None
    "Название фильтра в filterset. проставляется в метаклассе при создании."
    has_specs: bool = False
    "Показатель того, что фильтр имплементировал метод получения specs"
    has_facets: bool = False
    "Показатель того, что фильтр имплементировал метод получения facets"
    has_specs_columns: bool = False
    "Показатель того, что фильтр имплементировал метод получения specs в колонке основного запроса"
    has_facets_columns: bool = False
    "Показатель того, что фильтр имплементировал метод получения facets в колонке основного запроса"

    @abc.abstractmethod
    def filter(self, query: Select, value: Any) -> Select:
        """Метод реализующий фильтрацию"""
        ...


class Filter(BaseFilter):
    """Базовый фильтр для поля модели"""

    def __init__(
        self,
        model: Any,  # todo: typehint
        field: str,
        *,
        exclude: bool = False,
        nullable: bool = False,
    ) -> None:
        """
        :param model: Модель для фильтрации
        :param field: Поле модели для фильтрации
        :param exclude: Производить инвертированную фильтрацию
        :param nullable: Допускать пустые значения
        """
        super().__init__()
        self.model = model
        self.field = field
        self.exclude = exclude
        self.nullable = nullable

    def filter(self, query: Select, value: Any) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field) == value
        return query.where(~expression if self.exclude else expression)


class InFilter(Filter):
    def filter(self, query: Select, value: Sequence) -> Select:
        if not self.nullable and value in EMPTY_VALUES:
            return query

        expression = getattr(self.model, self.field).in_(value)
        return query.where(~expression if self.exclude else expression)
