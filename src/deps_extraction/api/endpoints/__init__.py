from ._internal import internal_router
from .debug import debug_router
from .document_type import document_type_router
from .extracted_data import extracted_data_router
from .healthcheck import healthcheck_router
from .service_info import service_info_router
from .v2.document_type import document_type_router as document_type_router_v2
from .v2.extracted_data import extracted_data_router as extracted_data_router_v2
