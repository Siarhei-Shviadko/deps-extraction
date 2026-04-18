from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from deps_extracted_data.serializers.v2 import (
    SaveExtractedDataRequest,
    SaveTableChunkRequest,
    SaveTableInfoRequest,
    SerializedExtractedData,
    SerializedExtractedField,
    TableChunkResponse,
    TableFieldChunk,
)
from fastapi import APIRouter, Body, Depends, Query, Response

from deps_extraction.api.endpoint_marker import MarkerRoute
from deps_extraction.api.endpoint_visibility import Visibility
from deps_extraction.application import ExtractedDataService
from deps_extraction.containers import Containers
from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataListFilterObject,
    ExtractedDataPaginationParamsObject,
)
from deps_extraction.infrastructure.repositories import ChunkedExtractedDataRepository

extracted_data_router = APIRouter(prefix="/extracted-data", route_class=MarkerRoute)


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
    return [SerializedExtractedData.from_model(edata) for edata in edata_list]


@extracted_data_router.get(
    "/{document_id}",
    response_model=SerializedExtractedData,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_extracted_data(
    document_id: int,
    rows_per_chunk: Optional[int] = Query(None, alias="rowsPerChunk", ge=1),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    if rows_per_chunk is not None:
        return SerializedExtractedData.from_model(application.get_paginated_extract_data(document_id, rows_per_chunk))
    return SerializedExtractedData.from_model(application.get_extracted_data(document_id))


@extracted_data_router.put(
    "/{document_id}",
    response_model=SerializedExtractedData,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def save_extracted_data(
    edata: SaveExtractedDataRequest,
    document_id: int,
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    res = application.save_extracted_data(
        document_id,
        extracted_fields=[field.to_model() for field in edata.fields],
        groups=[group.to_model() for group in edata.groups] if edata.groups else [],
    )
    return SerializedExtractedData.from_model(res)


@extracted_data_router.put(
    "/{document_id}/override",
    response_model=SerializedExtractedData,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def save_extracted_data_with_override(
    edata: SaveExtractedDataRequest,
    document_id: int,
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    res = application.save_extracted_data_with_override(
        document_id,
        extracted_fields=[field.to_model() for field in edata.fields],
        groups=[group.to_model() for group in edata.groups] if edata.groups else [],
    )
    return SerializedExtractedData.from_model(res)


@extracted_data_router.get(
    "/{document_id}/fields",
    response_model=list[SerializedExtractedField],
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_extracted_fields_by_codes(
    document_id: int,
    field_codes: list[str] = Query(alias="fieldCodes"),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    filtering = ExtractedDataFilterObject(document_id=document_id, field_codes=field_codes)
    fields = application.get_extracted_fields_by_filter(filtering)
    return [SerializedExtractedField.from_model(field) for field in fields]


@extracted_data_router.put(
    "/{document_id}/fields/{field_code}/table/info",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def put_table_info(
    document_id: int,
    field_code: str,
    table_info: SaveTableInfoRequest,
    repository: ChunkedExtractedDataRepository = Depends(Provide[Containers.repositories.chunked_extracted_data]),
):
    repository.put_table_info(table_info.to_dict(document_id=document_id, field_code=field_code))

    return Response(status_code=HTTPStatus.OK)


@extracted_data_router.put(
    "/{document_id}/fields/{field_code}/table/chunk",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def put_table_chunked_data(
    document_id: int,
    field_code: str,
    table_data: SaveTableChunkRequest,
    repository: ChunkedExtractedDataRepository = Depends(Provide[Containers.repositories.chunked_extracted_data]),
):
    repository.put_table_chunked_data(table_data.to_dicts(document_id, field_code), document_id)
    return Response(status_code=HTTPStatus.OK)


@extracted_data_router.get(
    "/{document_id}/fields/{field_code}/chunk",
    response_model=TableChunkResponse,
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def get_field_chunk(
    document_id: int,
    field_code: str,
    rows_per_chunk: int = Query(..., alias="rowsPerChunk", ge=1),
    rows_chunk: int = Query(..., alias="rowsChunk", ge=1),
    list_index: Optional[int] = Query(None, alias="listIndex", ge=0),
    repository: ChunkedExtractedDataRepository = Depends(Provide[Containers.repositories.chunked_extracted_data]),
):
    pagination_params = ExtractedDataPaginationParamsObject(
        rows_per_chunk=rows_per_chunk,
        rows_chunk=rows_chunk,
        list_index=list_index,
    )
    return repository.get_field_chunk(document_id, field_code, pagination_params)


@extracted_data_router.patch(
    "/{document_id}/fields/{field_code}",
    response_model=TableFieldChunk,
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_partial_extracted_data_field(
    document_id: int,
    field_code: str,
    table_data: TableFieldChunk,
    repository: ChunkedExtractedDataRepository = Depends(Provide[Containers.repositories.chunked_extracted_data]),
):
    repository.batch_partial_update_field(
        document_id,
        field_code,
        [data.to_partial_update_dict() for data in table_data.cells],
    )
    return table_data


@extracted_data_router.patch(
    "/{document_id}/fields/{field_code}/aliases",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_aliases(
    document_id: int,
    field_code: str,
    aliases: dict[str, str] = Body(..., alias="updatedAliases", embed=True),
    application: ExtractedDataService = Depends(Provide[Containers.application.extracted_data]),
):
    application.update_aliases(document_id=document_id, field_code=field_code, aliases=aliases)

    return Response(status_code=HTTPStatus.OK)
