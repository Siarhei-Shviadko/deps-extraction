from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from deps_extraction.api.endpoint_marker import MarkerRoute
from deps_extraction.api.endpoint_visibility import Visibility
from deps_extraction.containers import Datasources
from deps_extraction.extras.datasource import Database

healthcheck_router = APIRouter(route_class=MarkerRoute)


@healthcheck_router.get(
    "/healthcheck",
    tags=["Debug"],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def service_healthcheck(datasource: Database = Depends(Provide[Datasources.postgres_datasource])):
    """Check connection to database."""
    try:
        datasource.healthcheck()
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(status_code=status.HTTP_200_OK)
