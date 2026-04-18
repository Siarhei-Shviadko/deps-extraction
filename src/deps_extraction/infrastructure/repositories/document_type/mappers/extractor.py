from typing import Any

from deps_extraction.domain.model import EntityId, Extractor, ExtractorType

from .compliance import CompliancePolicyMapper
from .field import FieldMapper

__all__ = ["ExtractorMapper"]


class ExtractorMapper:
    @staticmethod
    def to_dict(extractor: Extractor, document_type_id: str) -> dict[str, Any]:
        return {
            "id": extractor.id(),
            "type": extractor.type.value,
            "fields": [FieldMapper.to_dict(field) for field in extractor.fields],
            "compliance_policies": [CompliancePolicyMapper.to_dict(policy) for policy in extractor.compliance_policies],
            "document_type_id": document_type_id,
        }

    @staticmethod
    def from_dict(extractor: dict[str, Any]) -> Extractor:
        fields = [FieldMapper.from_dict(field) for field in extractor["fields"]]
        compliance_policies = (
            [CompliancePolicyMapper.from_dict(policy) for policy in extractor["compliance_policies"]]
            if extractor["compliance_policies"] is not None
            else None
        )
        extractor_type = ExtractorType(extractor["type"])

        return Extractor(
            id_=EntityId(extractor["id"]),
            type_=extractor_type,
            fields=fields,
            compliance_policies=compliance_policies,
        )
