import random

import factory
from deps_extracted_data.model import (
    Bbox,
    CellCoordinates,
    CellRange,
    CharRange,
    SourceBboxCoordinates,
    SourceTableCoordinates,
    SourceTextCoordinates,
)
from faker import Faker

fake = Faker()

__all__ = [
    "BboxFactory",
    "SourceBboxCoordinatesFactory",
    "CellCoordinatesFactory",
    "CellRangeFactory",
    "CharRangeFactory",
    "SourceTextCoordinatesFactory",
    "SourceTableCoordinatesFactory",
]


class BboxFactory(factory.Factory):
    class Meta:
        model = Bbox

    x = factory.Faker("pyfloat", min_value=0, max_value=1)
    y = factory.Faker("pyfloat", min_value=0, max_value=1)
    w = factory.LazyAttribute(lambda obj: fake.pyfloat(min_value=0, max_value=1 - obj.x))
    h = factory.LazyAttribute(lambda obj: fake.pyfloat(min_value=0, max_value=1 - obj.y))


class SourceBboxCoordinatesFactory(factory.Factory):
    class Meta:
        model = SourceBboxCoordinates

    value = factory.Faker("uuid4")
    bboxes = factory.LazyFunction(lambda: [BboxFactory() for _ in range(random.randint(0, 2))])


class CellCoordinatesFactory(factory.Factory):
    class Meta:
        model = CellCoordinates

    row = factory.Faker("pyint", min_value=0)
    column = factory.Faker("pyint", min_value=0)


class CellRangeFactory(factory.Factory):
    class Meta:
        model = CellRange

    begin = factory.SubFactory(CellCoordinatesFactory)
    end = factory.LazyFunction(lambda: random.choice([None, CellCoordinatesFactory()]))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if end := kwargs.pop("end"):
            return model_class.with_end(begin=kwargs["begin"], end=end)
        return model_class(*args, **kwargs)


class SourceTableCoordinatesFactory(factory.Factory):
    class Meta:
        model = SourceTableCoordinates

    value = factory.Faker("uuid4")
    cell_ranges = factory.LazyFunction(lambda: [CellRangeFactory() for _ in range(random.randint(0, 2))])


class CharRangeFactory(factory.Factory):
    class Meta:
        model = CharRange

    begin = factory.Faker("pyint", min_value=0)
    end = factory.LazyAttribute(lambda obj: fake.pyint(min_value=obj.begin))


class SourceTextCoordinatesFactory(factory.Factory):
    class Meta:
        model = SourceTextCoordinates

    value = factory.Faker("uuid4")
    char_ranges = factory.LazyFunction(lambda: [CharRangeFactory() for _ in range(random.randint(0, 2))])
