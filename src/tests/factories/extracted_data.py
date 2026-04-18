import random

import factory
from deps_extracted_data.model import GenericData, TableMeta, TableRow

from .source_coordinates import (
    SourceBboxCoordinatesFactory,
    SourceTableCoordinatesFactory,
    SourceTextCoordinatesFactory,
)

__all__ = ["StringDataFactory", "TableRowFactory", "TableMetaFactory"]


class StringDataFactory(factory.Factory):
    class Meta:
        model = GenericData

    value = factory.Faker("word")
    confidence = factory.Faker("pyfloat", min_value=0, max_value=1)
    source_bbox_coordinates = factory.LazyFunction(
        lambda: random.choice([None, [SourceBboxCoordinatesFactory() for _ in range(random.randint(0, 2))]])
    )

    @factory.lazy_attribute
    def source_table_coordinates(self):
        if self.source_bbox_coordinates:
            return None
        return factory.LazyFunction(
            lambda: random.choice([None, [SourceTableCoordinatesFactory() for _ in range(random.randint(0, 2))]])
        )

    @factory.lazy_attribute
    def source_text_coordinates(self):
        if self.source_bbox_coordinates or self.source_table_coordinates:
            return None
        return factory.LazyFunction(
            lambda: random.choice([None, [SourceTextCoordinatesFactory() for _ in range(random.randint(0, 2))]])
        )


class TableMetaFactory(factory.Factory):
    class Meta:
        model = TableMeta

    chunks_total = factory.Faker("pyint", min_value=0)
    rows_total = factory.Faker("pyint", min_value=0)
    list_index = factory.Faker("pyint", min_value=0)


class TableRowFactory(factory.Factory):
    class Meta:
        model = TableRow

    y = factory.Faker("pyfloat", min_value=0, max_value=1)
