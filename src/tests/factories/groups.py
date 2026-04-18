import factory
from deps_extracted_data.model import Group

__all__ = ["GroupFactory"]


class GroupFactory(factory.Factory):
    class Meta:
        model = Group

    order = factory.Sequence(lambda x: x)
    name = factory.Faker("uuid4")
