from dataclasses import dataclass

from ..shared import Code
from .compliance_policy import CompliancePolicy
from .field import ExtractionField, FieldDescription, FieldProfile

__all__ = ["CompositeField"]


@dataclass(frozen=True)
class CompositeField:
    field: ExtractionField
    compliance_policy: CompliancePolicy

    @property
    def code(self) -> Code:
        return self.field.code

    @property
    def name(self) -> str:
        return self.field.name

    @property
    def profile(self) -> FieldProfile:
        return self.field.profile

    @property
    def description(self) -> FieldDescription:
        return self.field.profile.description

    @property
    def display_order(self) -> int:
        return self.field.display_order

    @property
    def required(self) -> bool:
        return self.field.required

    @property
    def read_only(self) -> bool:
        return self.compliance_policy.read_only

    @property
    def confidential(self) -> bool:
        return self.compliance_policy.confidential
