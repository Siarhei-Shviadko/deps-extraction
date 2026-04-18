from typing import Any, Optional

from deps_extraction.api.auth import get_current_user_tenant

__all__ = ["DocumentTypeCreationSagaData"]


class DocumentTypeCreationSagaData:
    def __init__(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        tenant_id: Optional[str] = None,
        document_type_id: Optional[str] = None,
    ) -> None:
        self.name = name
        self.tenant_id = tenant_id or get_current_user_tenant()
        self.description = description
        self.document_type_id = document_type_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "tenant_id": self.tenant_id,
            "description": self.description,
            "document_type_id": self.document_type_id,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "DocumentTypeCreationSagaData":
        return cls(
            name=raw_data["name"],
            description=raw_data.get("description"),
            tenant_id=raw_data.get("tenant_id"),
            document_type_id=raw_data.get("document_type_id"),
        )
