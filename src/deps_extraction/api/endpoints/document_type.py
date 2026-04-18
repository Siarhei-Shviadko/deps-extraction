from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, status

from deps_extraction.application import DocumentTypeService
from deps_extraction.containers import Containers

from ..auth import get_current_user_tenant
from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility
from ..serializers import SerializedDocumentType, SerializedDocumentTypes

__all__ = ["document_type_router"]

document_type_router = APIRouter(prefix="/document-types", route_class=MarkerRoute, tags=["Document Type"])


@document_type_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SerializedDocumentTypes,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_document_types(
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> SerializedDocumentTypes:
    document_types = application.get_document_types(tenant_id=tenant_id)
    return SerializedDocumentTypes.from_model(document_types)


@document_type_router.get(
    "/{documentTypeId}",
    status_code=status.HTTP_200_OK,
    response_model=SerializedDocumentType,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_document_type(
    document_type_id: str = Path(..., alias="documentTypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> SerializedDocumentType:
    document_type = application.get_document_type(document_type_id=document_type_id, tenant_id=tenant_id)
    return SerializedDocumentType.from_model(document_type)
