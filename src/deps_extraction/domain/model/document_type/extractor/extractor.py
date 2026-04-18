from typing import Optional

from ....exceptions import FieldAlreadyExistsError, FieldNotFound, InvariantViolation
from ...shared import Code, EntityId, ExtractorType, Guard, ImmutableCheck
from ..compliance_policy import CompliancePolicy
from ..constants import DEFAULT_FIELD_ORDER
from ..field import ExtractionField, FieldDescription, FieldProfile, FieldType

__all__ = ["Extractor"]


class Extractor:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    type = Guard[ExtractorType](ExtractorType)

    def __init__(
        self,
        id_: EntityId,
        type_: ExtractorType,
        fields: Optional[list[ExtractionField]] = None,
        compliance_policies: Optional[list[CompliancePolicy]] = None,
    ) -> None:
        self.id = id_
        self.type = type_
        self.field_storage = {field.code(): field for field in fields} if fields is not None else {}
        self.compliance_storage = (
            {policy.code(): policy for policy in compliance_policies} if compliance_policies is not None else {}
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Extractor) and other.id == self.id

    def __str__(self) -> str:
        return f"Extractor(id='{self.id()}', type='{self.type}')"

    def __repr__(self) -> str:
        return (
            f"Extractor(id={repr(self.id)}, type={repr(self.type)}, "
            f"fields={repr(list(self.field_storage.values()))}, "
            f"compliance_policies={repr(list(self.compliance_storage.values()))})"
        )

    @property
    def fields(self) -> list[ExtractionField]:
        return list(self.field_storage.values())

    @property
    def compliance_policies(self) -> list[CompliancePolicy]:
        return list(self.compliance_storage.values())

    def has_field_with_code(self, code: str) -> bool:
        return code in self.field_storage

    def find_field_with_code(self, code: str) -> ExtractionField:
        if (field := self.field_storage.get(code)) is None:
            raise FieldNotFound(doc_type_id=self.id(), field_code=code)

        return field

    def add_field(
        self,
        name: str,
        type_: FieldType,
        required: bool,
        description: Optional[FieldDescription] = None,
        confidential: Optional[bool] = None,
        read_only: Optional[bool] = None,
        code: Optional[str] = None,
        order: Optional[int] = None,
    ) -> ExtractionField:
        self.validate_field_constraints(code=code, name=name)

        field_code = Code(code)
        order = order if order is not None else DEFAULT_FIELD_ORDER

        self._register_field(
            code=field_code,
            name=name,
            type_=type_,
            required=required,
            description=description,
            order=order,
        )
        self._register_compliance_policy(code=field_code, confidential=confidential, read_only=read_only)

        return self.field_storage[field_code()]

    def update_field(
        self,
        code: str,
        name: Optional[str] = None,
        required: Optional[bool] = None,
        read_only: Optional[bool] = None,
        confidential: Optional[bool] = None,
        description: Optional[FieldDescription] = None,
        order: Optional[int] = None,
    ) -> ExtractionField:
        if any(parameter is not None for parameter in (name, required, description, order)):
            self._update_field(code=code, name=name, required=required, description=description, order=order)

        if any(parameter is not None for parameter in (read_only, confidential)):
            self._update_compliance_policy(code=code, read_only=read_only, confidential=confidential)

        return self.field_storage[code]

    def delete_field(self, code: str) -> None:
        for storage in (self.field_storage, self.compliance_storage):
            storage.pop(code, None)

    def validate_field_constraints(
        self,
        code: Optional[str],
        name: str,
    ) -> None:
        if code is not None and code in self.field_storage:
            raise FieldAlreadyExistsError(code=code)

        self.check_field_name_uniqueness(name)

    def check_field_name_uniqueness(self, name: str) -> None:
        if next((field for field in self.field_storage.values() if field.name == name), None) is not None:
            raise InvariantViolation(f"Field with name `{name}` already exists!")

    def _update_field(
        self,
        code: str,
        name: Optional[str] = None,
        required: Optional[bool] = None,
        description: Optional[FieldDescription] = None,
        order: Optional[int] = None,
    ) -> None:
        if (field := self.field_storage.get(code)) is None:
            raise FieldNotFound(doc_type_id=self.id(), field_code=code)

        if name is not None and name != field.name:
            self.check_field_name_uniqueness(name)

        field = field.create_updated(
            name=name,
            required=required,
            description=description,
            display_order=order,
        )

        self.field_storage[field.code()] = field

    def _update_compliance_policy(
        self,
        code: str,
        read_only: Optional[bool] = None,
        confidential: Optional[bool] = None,
    ) -> None:
        policy = self.compliance_storage[code]

        policy = policy.create_updated(read_only=read_only, confidential=confidential)
        self.compliance_storage[code] = policy

    def _register_field(
        self,
        code: Code,
        name: str,
        type_: FieldType,
        required: bool,
        order: int,
        description: Optional[FieldDescription] = None,
    ) -> None:
        field = ExtractionField(
            code=code,
            name=name,
            profile=FieldProfile(type_=type_, description=description),
            required=required,
            display_order=order,
        )
        self.field_storage[code()] = field

    def _register_compliance_policy(
        self,
        code: Code,
        read_only: Optional[bool] = None,
        confidential: Optional[bool] = None,
    ) -> None:
        policy = CompliancePolicy(
            code=code,
            read_only=read_only,
            confidential=confidential,
        )
        self.compliance_storage[code()] = policy
