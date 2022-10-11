import factory

from tests.async_alchemy_factory import AsyncSQLAlchemyModelFactory
from tests.models.base import GrandGrandParent, GrandParent, Item, Parent


class GrandGrandParentFactory(AsyncSQLAlchemyModelFactory):
    id = factory.Faker("uuid4")
    name = factory.Faker("pystr")

    class Meta:
        model = GrandGrandParent
        sqlalchemy_session_persistence = "commit"


class GrandParentFactory(AsyncSQLAlchemyModelFactory):
    id = factory.Faker("uuid4")
    name = factory.Faker("pystr")
    parent = factory.SubFactory(GrandGrandParentFactory)

    class Meta:
        model = GrandParent
        sqlalchemy_session_persistence = "commit"


class ParentFactory(AsyncSQLAlchemyModelFactory):
    id = factory.Faker("uuid4")
    name = factory.Faker("pystr")
    parent = factory.SubFactory(GrandParentFactory)
    date = factory.Faker("date_time_this_year")

    class Meta:
        model = Parent
        sqlalchemy_session_persistence = "commit"


class ItemFactory(AsyncSQLAlchemyModelFactory):
    id = factory.Faker("uuid4")
    parent = factory.SubFactory(ParentFactory)
    date = factory.Faker("date_time_this_year")
    area = factory.Faker("pyint")
    is_active = factory.Faker("pybool")
    title = factory.Faker("pystr")

    class Meta:
        model = Item
        sqlalchemy_session_persistence = "commit"
