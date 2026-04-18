from random import randint
from uuid import uuid4

from factory import Factory, Faker, LazyAttribute
from factory.fuzzy import FuzzyChoice

from deps_extraction.domain.model import (
    DocumentType,
    DocumentTypeId,
    EntityId,
    ExtractionType,
    TenantId,
)

from .extractor import ExtractorFactory

__all__ = ["DocumentTypeFactory"]


class DocumentTypeFactory(Factory):
    class Meta:
        model = DocumentType

    name = Faker("word")
    extraction_type = FuzzyChoice(list(ExtractionType))
    id_ = LazyAttribute(lambda _: DocumentTypeId())
    tenant_id = LazyAttribute(lambda _: TenantId(uuid4().hex))
    extractors = LazyAttribute(
        lambda self: {
            extractor_id: ExtractorFactory(id_=EntityId(extractor_id))
            for extractor_id in [uuid4().hex for _ in range(self.extractor_size)]
        }
    )

    class Params:
        extractor_size = LazyAttribute(lambda _: randint(0, 2))
