from typing import Type

from requests import Response

from deps_extraction.domain.exceptions import ExtractionException, RestClientError
from deps_extraction.extras.rest_client import BaseRESTClient, DEPSTokenAuth

from ..data_object_accessors import user

__all__ = ["GenericProxy"]


class GenericProxy(BaseRESTClient):
    exception: type[RestClientError]
    _HTTP_STATUS_EXCEPTION_TYPE_MAPPING: dict[int, Type[ExtractionException]] = {}

    def _set_authentication(self) -> None:
        self._session.auth = DEPSTokenAuth(user)

    def _check_response(self, response: Response) -> None:
        if not response.ok:
            self._logger.error(
                "Response to %s with payload %s failed with error %s",
                response.url,
                response.request.__dict__,
                response.content,
            )

            if (exception_type := self._HTTP_STATUS_EXCEPTION_TYPE_MAPPING.get(response.status_code)) is not None:
                raise exception_type(response.content)

            raise self.exception(response.content)
