from typing import Any

from deps_extraction.domain.model import Code
from deps_extraction.domain.model.document_type.compliance_policy import (
    CompliancePolicy,
)

__all__ = ["CompliancePolicyMapper"]


class CompliancePolicyMapper:
    @staticmethod
    def to_dict(compliance_policy: CompliancePolicy) -> dict[str, Any]:
        return {
            "code": compliance_policy.code(),
            "read_only": compliance_policy.read_only,
            "confidential": compliance_policy.confidential,
        }

    @staticmethod
    def from_dict(compliance_policy: dict[str, Any]) -> CompliancePolicy:
        return CompliancePolicy(
            code=Code(compliance_policy["code"]),
            read_only=compliance_policy["read_only"],
            confidential=compliance_policy["confidential"],
        )
