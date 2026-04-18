from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query, Response, status

from deps_extraction.application import AttachmentService, DocumentTypeService
from deps_extraction.containers import Containers
from deps_extraction.domain.model import FieldAttachment, RawUpdateField

from ...auth import get_current_user_tenant
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers.document_type import SerializedField
from ...serializers.v2 import (
    AttachExtractorRequest,
    AttachmentResponse,
    CreateFieldRequest,
    SerializedFields,
    UpdateFieldRequest,
    UpdateFieldsRequest,
)

__all__ = ["document_type_router"]

document_type_router = APIRouter(prefix="/document-types", route_class=MarkerRoute, tags=["Document Type"])


@document_type_router.post(
    "/{documentTypeId}/extraction-fields",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def create_field(
    create_field_request: CreateFieldRequest,
    document_type_id: str = Path(..., alias="documentTypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> SerializedField:
    field_description = create_field_request.description.to_model() if create_field_request.description else None
    created_field = application.create_field(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        name=create_field_request.name,
        type_=create_field_request.type,
        description=field_description,
        required=create_field_request.required,
        confidential=create_field_request.confidential,
        read_only=create_field_request.read_only,
        order=create_field_request.order,
        extractor_id=create_field_request.extractor_id,
        code=create_field_request.code,
    )

    return SerializedField.from_model(
        document_type_id=document_type_id,
        field=created_field,
    )


@document_type_router.patch(
    "/{documentTypeId}/extraction-fields/{fieldCode}",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def update_field(
    update_field_request: UpdateFieldRequest,
    document_type_id: str = Path(..., alias="documentTypeId"),
    field_code: str = Path(..., alias="fieldCode"),
    extractor_id: str | None = Query(None, alias="extractorId"),
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> SerializedField:
    field_description = update_field_request.description.to_model() if update_field_request.description else None
    updated_field = application.update_field(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        code=field_code,
        name=update_field_request.name,
        description=field_description,
        required=update_field_request.required,
        confidential=update_field_request.confidential,
        read_only=update_field_request.read_only,
        order=update_field_request.order,
        extractor_id=extractor_id,
    )

    return SerializedField.from_model(
        document_type_id=document_type_id,
        field=updated_field,
    )


@document_type_router.patch(
    "/{documentTypeId}/extraction-fields",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def update_fields(
    update_fields_request: UpdateFieldsRequest,
    document_type_id: str = Path(..., alias="documentTypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> SerializedFields:
    fields = [
        RawUpdateField(
            code=field.code,
            name=field.name,
            required=field.required,
            order=field.order,
            confidential=field.confidential,
            read_only=field.read_only,
            description=field.description.to_model() if field.description else None,
        )
        for field in update_fields_request.fields or []
    ]
    updated_fields = application.update_fields(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        fields=fields,
    )

    return SerializedFields.from_model(
        document_type_id=document_type_id,
        fields=updated_fields,
    )


@document_type_router.delete(
    "/{documentTypeId}/extraction-fields",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def delete_fields(
    document_type_id: str = Path(..., alias="documentTypeId"),
    field_codes: list[str] = Query(..., alias="fieldCodes"),
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> None:
    application.delete_fields(document_type_id=document_type_id, tenant_id=tenant_id, field_codes=field_codes)


@document_type_router.post(
    "/attach-extractor",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=AttachmentResponse,
)
@inject
def attach_extractor(
    attach_extractor_request: AttachExtractorRequest,
    tenant_id: str = Depends(get_current_user_tenant),
    application: AttachmentService = Depends(Provide[Containers.attachment_service]),
) -> AttachmentResponse:
    fields = [
        FieldAttachment(
            name=field.name,
            code=field.code,
            required=field.required,
            order=field.order,
            confidential=field.confidential,
            read_only=field.read_only,
            type=field.field_type,
            description=field.field_data.to_model() if field.field_data else None,
        )
        for field in attach_extractor_request.fields or []
    ]

    extractor = application.attach_extractor(
        document_type_name=attach_extractor_request.name,
        tenant_id=tenant_id,
        extractor_type=attach_extractor_request.extractor_type,
        description=attach_extractor_request.description,
        engine=attach_extractor_request.engine,
        language=attach_extractor_request.language,
        image_transformations=attach_extractor_request.image_transformations,
        extractor_id=attach_extractor_request.extractor_id,
        fields=fields,
    )

    return AttachmentResponse(
        command_channel=extractor.command_channel,
        document_type_id=extractor.document_type_id,
        extractor_id=extractor.extractor_id,
    )


@document_type_router.delete(
    "/{documentTypeId}/extractors/{extractorId}",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
def detach_extractor(
    document_type_id: str = Path(..., alias="documentTypeId"),
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
):
    application.detach_extractor(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
        extractor_id=extractor_id,
    )
