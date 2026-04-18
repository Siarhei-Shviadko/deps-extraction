import logging
from http import HTTPStatus
from typing import Optional

from deps_extraction.application.document_type.interfaces import IDocumentTypeProxy
from deps_extraction.constants import V1_PREFIX, V2_PREFIX
from deps_extraction.domain.exceptions import IllegalArgument

from ..generic import GenericProxy
from .exceptions import DocumentTypeProxyRequestError

__all__ = ["DocumentTypeProxy"]


class DocumentTypeProxy(GenericProxy, IDocumentTypeProxy):  # noqa: WPS338
    v1_url_suffix = f"/api/document-type{V1_PREFIX}/types"
    v2_url_suffix = f"/api/document-type{V2_PREFIX}/types"
    exception = DocumentTypeProxyRequestError
    _HTTP_STATUS_EXCEPTION_TYPE_MAPPING = {
        HTTPStatus.UNPROCESSABLE_ENTITY.value: IllegalArgument,
    }

    def __init__(self, base_url: str, timeout: int = 60, ssl_verify: bool = False) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document_type(self, name: str, description: Optional[str] = None) -> str:
        request_data = {
            "name": name,
            "description": description,
        }

        response = self._session.post(
            url=f"{self._base_url}{self.v2_url_suffix}",
            json=request_data,
            timeout=self._timeout,
            verify=self._verify,
        )

        self._check_response(response)

        document_type_data = response.json()

        return document_type_data["documentTypeId"]

    def delete_document_type(self, document_type_id: str) -> None:
        response = self._session.delete(
            url=f"{self._base_url}{self.v1_url_suffix}/{document_type_id}",
        )
        self._check_response(response)
