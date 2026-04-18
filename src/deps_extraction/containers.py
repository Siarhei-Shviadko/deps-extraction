from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import (
    SagaCommandProducer,
    SagaDataMapping,
    SagaInstanceFactory,
    SagaManagerFactory,
)
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_extraction.application import (
    AttachmentService,
    DocumentTypeService,
    ExtractedDataService,
    IDocumentTypeProxy,
)
from deps_extraction.constants import PROJECT_NAME
from deps_extraction.extras.datasource import Database, DBDialect, DBDriver
from deps_extraction.infrastructure.data_object_accessors import TenantDAO, user
from deps_extraction.infrastructure.proxies import DocumentTypeProxy
from deps_extraction.infrastructure.repositories import (
    ChunkedExtractedDataRepository,
    DocumentTypeRepository,
    ExtractedDataRepository,
    ExtractionWorkflowRepository,
    SagaInstanceRepository,
)
from deps_extraction.messaging.dispatcher import make_message_dispatcher
from deps_extraction.messaging.sagas import DocumentTypeCreationSaga
from deps_extraction.messaging.sagas_data import (
    DocumentTypeCreationSteps,
    make_saga_data_mapping,
)

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class DatabaseResource(resources.Resource):
    def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect,
        driver: DBDriver,
        require_secure_transport: bool,
        sslkey: str,
        sslcert: str,
        sslrootcert: str,
        sslmode: str,
    ) -> Database:
        db = Database(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            dialect=dialect,
            driver=driver,
            require_secure_transport=require_secure_transport,
            sslkey=sslkey,
            sslcert=sslcert,
            sslrootcert=sslrootcert,
            sslmode=sslmode,
        )
        db.connect()
        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        config.user,
        config.password,
        config.host,
        config.port,
        config.db,
        config.dialect,
        config.driver,
        config.require_secure_transport,
        sslkey=config.ssl.key,
        sslcert=config.ssl.cert,
        sslrootcert=config.ssl.rootcert,
        sslmode=config.ssl.mode,
    )


class DAO(containers.DeclarativeContainer):
    tenant_dao: providers.Singleton[TenantDAO] = providers.Singleton(
        TenantDAO,
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()
    dao = providers.DependenciesContainer()

    document_type: providers.Provider[DocumentTypeRepository] = providers.Singleton(
        DocumentTypeRepository,
        datasources.postgres_datasource,
    )

    extracted_data: providers.Provider[ExtractedDataRepository] = providers.Singleton(
        ExtractedDataRepository,
        database=datasources.postgres_datasource,
        tenant_dao=dao.tenant_dao,
    )
    chunked_extracted_data: providers.Provider[ChunkedExtractedDataRepository] = providers.Singleton(
        ChunkedExtractedDataRepository,
        database=datasources.postgres_datasource,
        tenant_dao=dao.tenant_dao,
    )
    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        datasources.postgres_datasource,
    )
    extraction_workflow: providers.Provider[ExtractionWorkflowRepository] = providers.Singleton(
        ExtractionWorkflowRepository,
        datasources.postgres_datasource,
    )


class ExternalServices(containers.DeclarativeContainer):
    config = providers.Configuration()

    document_type: providers.Provider[IDocumentTypeProxy] = providers.Singleton(
        DocumentTypeProxy,
        base_url=config.document_type.url,
        timeout=config.document_type.proxy_timeout,
        ssl_verify=config.ssl_verify,
    )


class SagaSteps(containers.DeclarativeContainer):
    external_services = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    domain_event_publisher: DomainEventPublisher = providers.Dependency()
    document_type_service: DocumentTypeService = providers.Dependency()

    document_type_creation: providers.Singleton[DocumentTypeCreationSteps] = providers.Singleton(
        DocumentTypeCreationSteps,
        document_type_service=document_type_service,
        document_type_proxy=external_services.document_type,
    )


class Application(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    domain_event_publisher: DomainEventPublisher = providers.Dependency()
    command_producer: CommandProducer = providers.Dependency()
    external_services = providers.DependenciesContainer()
    config = providers.Configuration()

    extracted_data: providers.Provider[ExtractedDataService] = providers.Singleton(
        ExtractedDataService,
        domain_event_publisher=domain_event_publisher,
        extracted_data_repository=repositories.extracted_data,
    )
    document_type: providers.Provider[DocumentTypeService] = providers.Singleton(
        DocumentTypeService,
        command_producer=command_producer,
        domain_event_publisher=domain_event_publisher,
        document_type_repository=repositories.document_type,
        extracted_data_repository=repositories.extracted_data,
        extraction_workflow_repository=repositories.extraction_workflow,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    current_user_tenant = providers.Callable(lambda: user.get()["organisation"])
    messaging_driver_settings = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )
    dao: providers.Container[DAO] = providers.Container(
        DAO,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        datasources=datasources,
        dao=dao,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )
    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )
    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    external_services: providers.Container[ExternalServices] = providers.Container(
        ExternalServices,
        config=config,
    )

    application: providers.Container[Application] = providers.Container(
        Application,
        config=config,
        repositories=repositories,
        domain_event_publisher=domain_event_publisher,
        command_producer=command_producer,
        external_services=external_services,
    )

    saga_command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )
    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )
    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        repositories.saga_instance,
        command_producer,
        messaging.consumer,
        saga_command_producer,
        saga_data_mapping,
    )
    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps,
        external_services=external_services,
        repositories=repositories,
        domain_event_publisher=domain_event_publisher,
        document_type_service=application.document_type,
    )
    sagas = providers.List(
        providers.Singleton(DocumentTypeCreationSaga, steps=saga_steps.document_type_creation),
    )
    saga_instance_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )

    attachment_service: providers.Provider[AttachmentService] = providers.Singleton(
        AttachmentService,
        document_type_repository=repositories.document_type,
        domain_event_publisher=domain_event_publisher,
        saga_instance_factory=saga_instance_factory,
        sagas=sagas,
    )
