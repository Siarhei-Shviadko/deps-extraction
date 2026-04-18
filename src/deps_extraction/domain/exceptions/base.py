__all__ = ["ExtractionException", "NotFoundError", "IllegalArgument", "BusinessException", "RestClientError"]


class ExtractionException(Exception):
    code = "extraction_exception"


class BusinessException(ExtractionException):
    code = "business_exception"


class NotFoundError(BusinessException):
    code = "not_found_error"


class IllegalArgument(BusinessException):
    code = "illegal_argument"


class RestClientError(ExtractionException):
    code = "rest_client_error"
