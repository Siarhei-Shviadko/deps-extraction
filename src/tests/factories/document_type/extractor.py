from random import randint

from factory import Factory, LazyAttribute
from factory.fuzzy import FuzzyChoice

from deps_extraction.domain.model import Code, EntityId, Extractor, ExtractorType

from .field import ExtractionFieldFactory

__all__ = ["ExtractorFactory"]


class ExtractorFactory(Factory):
    class Meta:
        model = Extractor

    id_ = LazyAttribute(lambda _: EntityId())
    type_ = FuzzyChoice(list(ExtractorType))
    fields = LazyAttribute(
        lambda self: [ExtractionFieldFactory(code=self.field_code[i]) for i in range(self.fields_size)],
    )

    class Params:
        fields_size = LazyAttribute(lambda _: randint(0, 5))
        field_code = LazyAttribute(lambda self: [Code() for _ in range(self.fields_size)])
