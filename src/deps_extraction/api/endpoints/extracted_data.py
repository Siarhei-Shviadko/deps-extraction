from typing import Any, Optional

from dependency_injector.wiring import Provide, inject
from deps_extracted_data.serializers.v1 import (
    SerializedExtractedData,
    SerializedExtractedField,
)
from fastapi import APIRouter, Body, Depends, Query

from deps_extraction.api.endpoint_marker import MarkerRoute
from deps_extraction.api.endpoint_visibility import Visibility
from deps_extraction.application import ExtractedDataService
from deps_extraction.containers import Containers
from deps_extraction.domain.dtos import ExtractedDataListFilterObject

from ..helpers import build_extracted_data

extracted_data_router = APIRouter(prefix="/extracted-data", tags=["Extracted Data"], route_class=MarkerRoute)


@extracted_data_router.get(
    "/",
    response_model=list[SerializedExtractedData],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_list_extracted_data(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    document_ids: Optional[list[int]] = Query(None, alias="documentIds"),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    filtering = ExtractedDataListFilterObject(
        document_ids=document_ids,
        limit=limit,
        offset=offset,
    )
    edata_list = application.get_extracted_data_list_by_filter(filtering)
    return [
        SerializedExtractedData(
            document_id=edata.document_id,
            fields=[SerializedExtractedField.from_model(field) for field in edata.fields],
        )
        for edata in edata_list
    ]


@extracted_data_router.get(
    "/{document_id}",
    response_model=list[SerializedExtractedField],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_extracted_data(
    document_id: int,
    rows_per_chunk: Optional[int] = Query(None, alias="rowsPerChunk", ge=1),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    if rows_per_chunk is not None:
        return SerializedExtractedData.from_model(
            application.get_paginated_extract_data(document_id, rows_per_chunk),
        ).fields
    return SerializedExtractedData.from_model(application.get_extracted_data(document_id)).fields


@extracted_data_router.put(
    "/{document_id}",
    response_model=list[SerializedExtractedField],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def save_extracted_data(
    document_id: int,
    extracted_data: dict[str, Any] = Depends(build_extracted_data),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    edata = application.save_extracted_data(
        document_id,
        extracted_fields=extracted_data["fields"],
        groups=extracted_data["groups"],
    )

    return SerializedExtractedData.from_model(edata).fields


@extracted_data_router.delete(
    "/{document_id}",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def delete_extracted_data(
    document_id: int,
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    application.delete_extracted_data(document_id)
    return {"message": "Successfully deleted."}


@extracted_data_router.put(
    "/{document_id}/field",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def save_extracted_data_field(
    document_id: int,
    field: SerializedExtractedField,
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    edata_field = application.save_field(document_id, field.to_model())
    return SerializedExtractedField.from_model(edata_field)


@extracted_data_router.delete(
    "/{document_id}/fields",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def delete_extracted_fields(
    document_id: int,
    field_codes: list[str] = Body(..., alias="fieldPks", min_items=1, embed=True),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    application.delete_extracted_fields(document_id=document_id, field_codes=field_codes)
    return {"message": "Successfully deleted."}
