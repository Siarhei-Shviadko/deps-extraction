from uuid import uuid4

from factory import Factory, Faker, LazyAttribute, SubFactory, fuzzy

from deps_extraction.domain.model import Code, ExtractionField

from .profile import FieldProfileFactory

__all__ = ["ExtractionFieldFactory"]


class ExtractionFieldFactory(Factory):
    class Meta:
        model = ExtractionField

    code = LazyAttribute(lambda _: Code())
    name = LazyAttribute(lambda _: uuid4().hex)
    profile = SubFactory(FieldProfileFactory)
    required = Faker("boolean")
    display_order = fuzzy.FuzzyInteger(0, 10)
