from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_extraction.extras.datasource import DatabaseSettings
from deps_extraction.extras.settings import ServiceInfoSettings


class DocumentTypeProxySettings(BaseSettings):
    url: str
    proxy_timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="DOCUMENT_TYPE_")


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    info: ServiceInfoSettings = ServiceInfoSettings()
    database: DatabaseSettings = DatabaseSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    document_type: DocumentTypeProxySettings = DocumentTypeProxySettings()

    documentation_enabled: bool = True
    ssl_verify: bool = False
    instrumentation_enabled: bool = False

    default_command_channel: str = Field(validation_alias="DEFAULT_COMMAND_CHANNEL")

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("messaging_driver_settings", mode="before")
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()

        raise ValueError(f"Driver {driver} is not implemented")
