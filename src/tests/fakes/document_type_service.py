from uuid import uuid4

from deps_extraction.application import IDocumentTypeProxy

__all__ = ["FakeDocumentTypeProxy"]


class FakeDocumentTypeProxy(IDocumentTypeProxy):
    def create_document_type(self, *args, **kwargs) -> str:
        return uuid4().hex

    def delete_document_type(self, document_type_id: str) -> None:
        pass
