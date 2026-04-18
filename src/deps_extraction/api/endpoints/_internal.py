from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from deps_extraction.application import DocumentTypeService
from deps_extraction.containers import Containers

__all__ = ["internal_router"]

internal_router = APIRouter(prefix="/fields")


@internal_router.get(
    "",
    status_code=status.HTTP_200_OK,
)
@inject
def get_all_extraction_fields(
    application: DocumentTypeService = Depends(Provide[Containers.application.document_type]),
) -> list:
    return application.get_all_extraction_fields()
