import inspect
from typing import Any, Coroutine, List, Type, TypeVar

from factory.base import Factory, FactoryOptions, OptionDefault
from sqlalchemy.ext.asyncio import AsyncSession

SESSION_PERSISTENCE_COMMIT = "commit"
SESSION_PERSISTENCE_FLUSH = "flush"
VALID_SESSION_PERSISTENCE_TYPES = [
    None,
    SESSION_PERSISTENCE_COMMIT,
    SESSION_PERSISTENCE_FLUSH,
]


class AsyncSQLAlchemyOptions(FactoryOptions):
    def _check_sqlalchemy_session_persistence(self, meta: Any, value: Any) -> None:
        if value not in VALID_SESSION_PERSISTENCE_TYPES:
            raise TypeError(
                "%s.sqlalchemy_session_persistence must be one of %s, got %r"
                % (meta, VALID_SESSION_PERSISTENCE_TYPES, value)
            )

    def _build_default_options(self) -> List[OptionDefault]:
        return super()._build_default_options() + [
            OptionDefault(
                "sqlalchemy_session_persistence",
                None,
                inherit=True,
                checker=self._check_sqlalchemy_session_persistence,
            ),
        ]


Model = TypeVar("Model")


class AsyncSQLAlchemyModelFactory(Factory):
    """Base class for facotries."""

    _session: AsyncSession
    _options_class = AsyncSQLAlchemyOptions

    class Meta:
        abstract = True
        exclude = ("_session",)

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Create a model.
        This function creates model with given arguments
        and stores it in current session.
        """
        if cls._session is None:
            raise RuntimeError("No session provided.")

        return cls._save(model_class, cls._session, args, kwargs)

    @classmethod
    def _save(
        cls, model_class: Type[Model], session: AsyncSession, args: Any, kwargs: Any
    ) -> Coroutine[Any, Any, Model]:
        session_persistence = cls._meta.sqlalchemy_session_persistence

        async def maker_coroutine() -> Model:
            for key, value in kwargs.items():
                if inspect.isawaitable(value):
                    kwargs[key] = await value

            obj = model_class(*args, **kwargs)
            session.add(obj)
            if session_persistence == SESSION_PERSISTENCE_FLUSH:
                await session.flush()
            elif session_persistence == SESSION_PERSISTENCE_COMMIT:
                await session.commit()
                await session.refresh(obj)
            return obj

        return maker_coroutine()

    @classmethod
    async def create_batch(cls, size: int, **kwargs: Any) -> List[Model]:
        return [await cls.create(**kwargs) for _ in range(size)]
