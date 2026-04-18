import logging
from http import HTTPStatus

from deps_extracted_data.exceptions.base import IllegalArgument as VendorIllegalArgument
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from deps_extraction.api.serializers.error import ErrorSerializer
from deps_extraction.domain.exceptions import (
    AttachmentExtractorConflict,
    ExtractedDataForbidden,
    ExtractionException,
    IllegalArgument,
    NotFoundError,
)

__all__ = ["register_error_handler", "json_extraction_error_handler"]

_logger = logging.getLogger(__name__)


def json_extraction_error_handler(error: ExtractionException, status_code: int):
    error_message = ErrorSerializer(code=error.code, message=str(error)).model_dump()
    return JSONResponse(status_code=status_code, content=error_message)


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(ExtractionException)
    def handle_extraction_exception(req: Request, error: ExtractionException):  # noqa: WPS430
        _logger.error(f"Domain exception occurred: {str(error)}")

        mapper = [
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (ExtractedDataForbidden, HTTPStatus.FORBIDDEN),
            (IllegalArgument, HTTPStatus.UNPROCESSABLE_ENTITY),
            (AttachmentExtractorConflict, HTTPStatus.CONFLICT),
            (ExtractionException, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_extraction_error_handler(error, status_code)

    @app.exception_handler(ValidationError)
    def bad_request(req: Request, exc: ValidationError):  # noqa: WPS430
        _logger.warning(f"Validation error occurred: {str(exc)}")

        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorSerializer(code="bad_request", message=str(exc)).model_dump(),
        )

    @app.exception_handler(VendorIllegalArgument)
    def handle_vendor_illegal_argument(req: Request, exc: VendorIllegalArgument) -> JSONResponse:  # noqa: WPS430
        _logger.warning(f"Vendor validation error occurred: {str(exc)}")

        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=ErrorSerializer(code=exc.code, message=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):  # noqa: WPS430
        _logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorSerializer(code="unhandled_error", message=str(error)).model_dump(),
        )
