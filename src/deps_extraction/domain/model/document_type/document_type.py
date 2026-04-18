import contextlib
from itertools import chain
from typing import Any, Optional

from deps_message_flow.events.common import DomainEvent

from ...events import (
    ExtractorAttached,
    ExtractorDetached,
    ExtractorFieldCreated,
    ExtractorFieldDeleted,
    ExtractorFieldUpdated,
)
from ...exceptions import (
    AttachmentExtractorConflict,
    ExtractionWorkflowCreationError,
    ExtractorNotFound,
    FieldNotFound,
    InvariantViolation,
)
from ..extraction_workflow import ExtractionWorkflow, ExtractionWorkflowBuilder
from ..shared import (
    DocumentTypeId,
    EntityId,
    ExtractionFieldData,
    ExtractionType,
    ExtractorType,
    FormatCheck,
    Guard,
    ImmutableCheck,
    LengthCheck,
    TenantId,
)
from .attachment_field import FieldAttachment
from .compliance_policy import CompliancePolicy
from .composite_field import CompositeField
from .extractor import Extractor
from .field import ExtractionField, FieldDescription, FieldType, RawUpdateField

__all__ = ["DocumentType"]


class DocumentType:
    id = Guard[DocumentTypeId](DocumentTypeId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    extraction_type = Guard[ExtractionType](ExtractionType)
    name = Guard[str](
        str,
        ImmutableCheck(),
        FormatCheck(r"^(?![- ]+)(?!.*[- ]+$)[\w-]+( [\w-]+)*$"),
        LengthCheck(max_length=250),
    )
    extractors = Guard[dict[str, Extractor]](dict)

    def __init__(
        self,
        id_: DocumentTypeId,
        tenant_id: TenantId,
        name: str,
        extraction_type: ExtractionType,
        extractors: Optional[dict[str, Extractor]] = None,
        *,
        events: Optional[list[DomainEvent]] = None,
    ) -> None:
        self.id = id_
        self.tenant_id = tenant_id
        self.name = name

        self.extractors = extractors or {}
        self.extraction_type = extraction_type

        self._events = events or []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DocumentType) and other.id == self.id

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.id = },",
                f"{self.tenant_id = },",
                f"{self.name = },",
                f"{self.extraction_type = },",
                f"fields={self.composite_fields = },",
                f"{self._events = }>",
            ),
        )

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

    @property
    def composite_fields(self) -> list[CompositeField]:
        return [
            self._build_composite_field_by_code(extractor_id=extractor.id(), code=field.code())
            for extractor in self.extractors.values()
            for field in extractor.fields
        ]

    @property
    def compliance_policies(self) -> list[CompliancePolicy]:
        return list(chain.from_iterable(extractor.compliance_policies for extractor in self.extractors.values()))

    @property
    def extraction_fields(self) -> list[ExtractionField]:
        return list(chain.from_iterable(extractor.fields for extractor in self.extractors.values()))

    @property
    def command_channel(self) -> str:
        return f"{self.name}-{self.tenant_id()}"

    @property
    def extraction_fields_data(self) -> list[ExtractionFieldData]:
        fields_data: list[ExtractionFieldData] = []

        for extractor in self.extractors.values():
            for field in extractor.fields:
                compliency_policy = extractor.compliance_storage.get(field.code())

                fields_data.append(
                    ExtractionFieldData(
                        document_type_id=self.id(),
                        code=field.code(),
                        name=field.name,
                        type=field.type,
                        required=field.required,
                        order=field.display_order,
                        confidential=compliency_policy.confidential if compliency_policy else False,
                        read_only=compliency_policy.read_only if compliency_policy else False,
                        description=field.description.to_dict(),
                    ),
                )

        return fields_data

    def has_field_with_code(self, code: str) -> bool:
        return any(extractor.has_field_with_code(code) for extractor in self.extractors.values())

    def find_field_with_code(self, code: str) -> ExtractionField:
        for extractor in self.extractors.values():
            if extractor.has_field_with_code(code):
                return extractor.find_field_with_code(code)

        raise FieldNotFound(self.id(), code)

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
        extractor_id: Optional[str] = None,
    ) -> CompositeField:
        self._validate_field_constraints(code=code, name=name)

        extractor = self._get_extractor_by(id_=extractor_id)
        field = extractor.add_field(
            name=name,
            type_=type_,
            required=required,
            description=description,
            confidential=confidential,
            read_only=read_only,
            code=code,
            order=order,
        )
        compliency_policy = extractor.compliance_storage[field.code()]
        self._events.append(
            ExtractorFieldCreated(
                code=field.code(),
                name=name,
                document_type_code=self.id(),
                extractor_id=extractor.id(),
                extractor_type=self._convert_extractor_type(extractor.type),
                field_type=type_,
                required=field.required,
                order=field.display_order,
                confidential=compliency_policy.confidential,
                read_only=compliency_policy.read_only,
                description=field.profile.description,
            ),
        )

        return self._build_composite_field_by_code(extractor_id=extractor.id(), code=field.code())

    def update_field(
        self,
        code: str,
        name: Optional[str] = None,
        required: Optional[bool] = None,
        read_only: Optional[bool] = None,
        confidential: Optional[bool] = None,
        description: Optional[FieldDescription] = None,
        order: Optional[int] = None,
        extractor_id: Optional[str] = None,
    ) -> CompositeField:
        extractor = self._get_extractor_by(id_=extractor_id, code=code)

        if name is not None:
            self._validate_field_constraints(code=None, name=name, exclude_extractor=extractor)

        extractor.update_field(
            code=code,
            name=name,
            required=required,
            read_only=read_only,
            confidential=confidential,
            description=description,
            order=order,
        )
        self._events.append(
            ExtractorFieldUpdated(
                code=code,
                name=extractor.field_storage[code].name,
                document_type_code=self.id(),
                extractor_id=extractor.id(),
                extractor_type=self._convert_extractor_type(extractor.type),
                field_type=extractor.field_storage[code].profile.type,
                required=extractor.field_storage[code].required,
                order=extractor.field_storage[code].display_order,
                confidential=extractor.compliance_storage[code].confidential,
                read_only=extractor.compliance_storage[code].read_only,
                description=extractor.field_storage[code].profile.description,
            ),
        )
        return self._build_composite_field_by_code(extractor_id=extractor.id(), code=code)

    def update_fields(self, fields: list[RawUpdateField]) -> list[CompositeField]:
        return [
            self.update_field(
                code=field["code"],
                name=field["name"],
                required=field["required"],
                read_only=field["read_only"],
                confidential=field["confidential"],
                description=field["description"],
                order=field["order"],
            )
            for field in fields
        ]

    def delete_field(self, code: str, extractor_id: Optional[str] = None) -> None:
        with contextlib.suppress(ExtractorNotFound):
            extractor = self._get_extractor_by(id_=extractor_id, code=code)
            extractor.delete_field(code)
            self._events.append(
                ExtractorFieldDeleted(
                    code=code,
                    document_type_code=self.id(),
                    extractor_id=extractor.id(),
                    extractor_type=self.extraction_type,
                ),
            )

    def delete_fields(self, field_codes: list[str]) -> None:
        for field_code in field_codes:
            self.delete_field(field_code)

    def update_extractor_info(
        self,
        extractor_id: str,
        extractor_type: str,
        description: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        image_transformations: Optional[list[str]] = None,
    ):
        self._events.append(
            ExtractorAttached(
                extractor_id=extractor_id,
                document_type_id=self.id(),
                extraction_type=extractor_type,
                language=language,
                engine=engine,
                image_transformations=image_transformations,
                description=description,
            ),
        )

    def attach_extractor(
        self,
        type_: ExtractorType,
        fields: list[FieldAttachment],
        description: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        image_transformations: Optional[list[str]] = None,
        extractor_id: Optional[str] = None,
    ) -> Extractor:
        should_create_extractor = extractor_id is None or extractor_id not in self.extractors
        if should_create_extractor and self._extractor_can_be_attached(type_):
            extractor = Extractor(
                id_=EntityId(extractor_id),
                type_=type_,
            )
            self.extractors[extractor.id()] = extractor

            self._handle_extractor_initialization(
                extractor=extractor,
                description=description,
                engine=engine,
                language=language,
                image_transformations=image_transformations,
            )
        else:
            extractor = self._get_extractor_by(id_=extractor_id)
            self._validate_extractor_type(existing_type=extractor.type, new_type=type_)

        self._track_fields_changes(extractor, fields)
        return extractor

    def detach_extractor(self, extractor_id: str) -> None:
        if extractor := self.extractors.get(extractor_id):
            if extractor.type == ExtractorType.LLM:
                self.extractors.pop(extractor_id)
                self._events.append(
                    ExtractorDetached(
                        document_type_id=self.id(),
                        extractor_id=extractor.id(),
                        extractor_type=extractor.type,
                    ),
                )
                return
            raise InvariantViolation("Only LLM Extractor can be detached.")
        raise ExtractorNotFound(document_type=self.id())

    def copy_fields_from(self, source_document_type: "DocumentType") -> None:
        self._can_copy_fields_from(source_document_type)
        source_extractor = next(
            filter(
                lambda extractor: extractor.type == ExtractorType.TEMPLATE,
                source_document_type.extractors.values(),
            ),
        )

        for source_field in source_extractor.fields:
            self.add_field(
                code=source_field.code(),
                name=source_field.name,
                type_=source_field.profile.type,
                required=source_field.required,
                description=source_field.profile.description,
                confidential=source_extractor.compliance_storage[source_field.code()].confidential,
                read_only=source_extractor.compliance_storage[source_field.code()].read_only,
                order=source_field.display_order,
            )

    def create_workflow_for(
        self,
        document_id: str,
        tenant_id: str,
        correlation_headers: dict[str, Any],
        extra_headers: dict[str, Any],
        template_version_id: Optional[str] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
    ) -> ExtractionWorkflow:
        self._ensure_workflow_creation_possible()
        builder = ExtractionWorkflowBuilder(
            document_id=document_id,
            tenant_id=tenant_id,
            document_type_id=self.id(),
            command_channel=self.command_channel,
            correlation_headers=correlation_headers,
            extra_headers=extra_headers,
            template_version_id=template_version_id,
            language=language,
            engine=engine,
            llm_type=llm_type,
        )
        # For supporting backward capabilities llm extractors have to go firstly.
        # Old Plugins reply to workflow-manager
        sorted_extractors = sorted(
            self.extractors.values(),
            key=lambda extractor: int(extractor.type != ExtractorType.LLM),
        )
        for sorted_extractor in sorted_extractors:
            builder.with_step_for(extractor_id=sorted_extractor.id(), extractor_type=sorted_extractor.type)

        return builder.build()

    def move_fields_between_extractors(
        self,
        source_extractor_id: str,
        target_extractor_id: str,
        fields_codes: list[str],
    ) -> None:
        source_extractor = self.extractors.get(source_extractor_id)
        target_extractor = self.extractors.get(target_extractor_id)

        if not source_extractor or not target_extractor:
            raise ExtractorNotFound(document_type=self.id())

        for code in fields_codes:
            field = source_extractor.field_storage.get(code)
            target_extractor.add_field(
                code=field.code(),
                name=field.name,
                type_=field.profile.type,
                required=field.required,
                description=field.profile.description,
                confidential=source_extractor.compliance_storage[field.code()].confidential,
                read_only=source_extractor.compliance_storage[field.code()].read_only,
                order=field.display_order,
            )

            source_extractor.delete_field(code)

    def _set_extraction_type(self, type_: str) -> None:
        self.extraction_type = ExtractionType(type_)

    def _ensure_workflow_creation_possible(self) -> None:
        if not self.extractors:
            raise ExtractionWorkflowCreationError(
                "Extraction workflow cannot be created because no extractors are available.",
            )

    def _handle_extractor_initialization(
        self,
        extractor: Extractor,
        description: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        image_transformations: Optional[list[str]] = None,
    ) -> None:
        if self._should_extraction_info_be_updated(extractor.type):
            self._set_extraction_type(type_=self._convert_extractor_type(extractor.type))

            self.update_extractor_info(
                extractor_id=extractor.id(),
                extractor_type=self._convert_extractor_type(extractor.type),
                language=language,
                engine=engine,
                description=description,
                image_transformations=image_transformations,
            )

    def _should_extraction_info_be_updated(self, extractor_type: ExtractorType) -> bool:
        return bool(
            (self.extraction_type is ExtractionType.NON and extractor_type is not ExtractorType.LLM)
            or len(self.extractors) == 1,
        )

    def _extractor_can_be_attached(self, type_: ExtractorType) -> bool:
        if self.extraction_type not in {ExtractionType.NON, ExtractionType.PLUGIN} and type_ != ExtractorType.LLM:
            raise AttachmentExtractorConflict(
                document_type=self.name,
                new_extractor=type_.value,
                previous_extractor=self.extraction_type.value,
            )

        if self.extraction_type == ExtractionType.PLUGIN and type_ not in {
            ExtractorType.PLUGIN,
            ExtractorType.LLM,
        }:
            raise AttachmentExtractorConflict(
                document_type=self.name,
                new_extractor=type_.value,
                previous_extractor=self.extraction_type.value,
            )

        return not bool(type_ is ExtractorType.PLUGIN and self.extraction_type is ExtractionType.PLUGIN)

    def _can_copy_fields_from(self, source_document_type: "DocumentType") -> None:
        """DocumentType has to allow copying only for document types that have a Template extraction type"""
        if (
            self.extraction_type == ExtractionType.TEMPLATE
            and source_document_type.extraction_type == ExtractionType.TEMPLATE
        ):
            return
        raise InvariantViolation("Copying fields possible only for document types that have Template extraction type.")

    def _track_fields_changes(
        self,
        extractor: Extractor,
        new_fields: list[FieldAttachment],
    ) -> None:
        new_fields_by_codes = {field.code: field for field in new_fields}
        composite_fields_by_code = {field.code(): field for field in self.composite_fields}

        old_fields_codes = set(extractor.field_storage.keys())

        new_fields_codes = list(new_fields_by_codes.keys())

        fields_to_delete = old_fields_codes.difference(new_fields_by_codes)
        fields_to_create = [code for code in new_fields_codes if code not in old_fields_codes]
        fields_to_update = [
            code
            for code in old_fields_codes.intersection(new_fields_codes)
            if new_fields_by_codes[code].has_difference_with_composite_field(composite_fields_by_code[code])
        ]

        for field_code_to_delete in fields_to_delete:
            self.delete_field(code=field_code_to_delete)

        for field_code_to_create in fields_to_create:
            field = new_fields_by_codes[field_code_to_create]
            self.add_field(
                code=field.code,
                name=field.name,
                type_=field.type,
                required=field.required,
                description=field.description,
                confidential=field.confidential,
                read_only=field.read_only,
                order=field.order,
                extractor_id=extractor.id(),
            )

        for field_code_to_update in fields_to_update:
            field = new_fields_by_codes[field_code_to_update]
            self.update_field(
                code=field.code,
                name=field.name,
                required=field.required,
                description=field.description,
                confidential=field.confidential,
                read_only=field.read_only,
                order=field.order,
                extractor_id=extractor.id(),
            )

    def _build_composite_field_by_code(self, extractor_id: str, code: str) -> CompositeField:
        extractor = self.extractors[extractor_id]
        return CompositeField(
            field=extractor.field_storage[code],
            compliance_policy=extractor.compliance_storage[code],
        )

    def _get_extractor_by(
        self,
        id_: Optional[str],
        code: Optional[str] = None,
    ) -> Extractor:
        if id_:
            extractor = self.extractors.get(id_)
        elif code:
            extractor = next(filter(lambda elem: code in elem.field_storage, self.extractors.values()), None)
        else:
            extractor = next(
                filter(lambda elem: elem.type is not ExtractorType.LLM, reversed(self.extractors.values())),
                None,
            )

        if extractor:
            return extractor

        raise ExtractorNotFound(document_type=self.id())

    def _validate_field_constraints(
        self,
        code: Optional[str],
        name: str,
        exclude_extractor: Optional[Extractor] = None,
    ) -> None:
        filtered_extractors = list(filter(lambda e: e != exclude_extractor, self.extractors.values()))
        for extractor in filtered_extractors:
            extractor.validate_field_constraints(code=code, name=name)

    def _convert_extractor_type(self, type_: ExtractorType) -> str:
        return ExtractionType.NON if type_ == ExtractorType.LLM else type_

    def _validate_extractor_type(self, existing_type: ExtractorType, new_type: ExtractorType) -> None:
        if existing_type != new_type:
            raise AttachmentExtractorConflict(
                document_type=self.name,
                new_extractor=new_type.value,
                previous_extractor=existing_type.value,
            )
