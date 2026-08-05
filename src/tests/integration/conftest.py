import pytest

from deps_extraction.domain.interfaces import IExtractionWorkflowRepository


@pytest.fixture(autouse=True)
def session(containers):
    database = containers.datasources.postgres_datasource()
    connection = database.get_connection()

    class TrapForThreadLocalConnections:
        """
        This class is used instead of threading.local in Database, for allowing connection transactions management
        """

        connection = None

    TrapForThreadLocalConnections.connection = connection
    connection.begin()
    transaction = connection.begin_nested()
    database._registry = TrapForThreadLocalConnections
    try:
        yield
    finally:
        transaction.rollback()
    database.close()


@pytest.fixture
def document_type_repository(repositories):
    yield repositories.document_type()


@pytest.fixture
def extracted_data_repository(repositories):
    yield repositories.extracted_data()


@pytest.fixture
def chuncked_repository(repositories):
    yield repositories.chunked_extracted_data()


@pytest.fixture
def extracted_data_service(application):
    return application.extracted_data()


@pytest.fixture
def domain_event_publisher(containers):
    return containers.domain_event_publisher()


@pytest.fixture
def extraction_workflow_repository(repositories) -> IExtractionWorkflowRepository:
    return repositories.extraction_workflow()
