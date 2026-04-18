import json
import logging
from functools import partial
from typing import Any, Callable, Optional
from uuid import uuid4

from deps_message_flow.commands.common import (
    Command,
    CommandMessageHeaders,
    CommandReplyOutcome,
    ReplyMessageHeaders,
)

from deps_extraction.constants import COMMANDS_REPLIES_CHANNEL

from ....events import (
    ExtractDocument,
    PerformCloudNativeExtraction,
    PerformExtractionReply,
    PerformLLMExtraction,
    PerformPrototypeExtraction,
    PerformTemplateExtraction,
)
from ....types import RawCommand
from ...shared import CloudNativeExtractors, EntityId, ExtractorType
from .destination import Destination
from .extraction_step import ExtractionStep

__all__ = ["ExtractionStepFactory"]


class ExtractionStepFactory:
    def __init__(
        self,
        workflow_id: str,
        tenant_id: str,
        document_id: str,
        document_type_id: str,
        command_channel: str,
        correlation_headers: dict[str, str],
        extra_headers: dict[str, Any],
        template_version_id: Optional[str] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
    ) -> None:
        self._workflow_id = workflow_id
        self._document_id = document_id
        self._document_type_id = document_type_id
        self._tenant_id = tenant_id
        self._command_channel = command_channel
        self._template_version_id = template_version_id
        self._language = language
        self._engine = engine
        self._llm_type = llm_type
        self._correlation_headers = correlation_headers
        self._extra_headers = extra_headers
        self._correlation_destination = self._get_correlation_destination()
        self._destination = COMMANDS_REPLIES_CHANNEL

        self._extraction_commands: dict[ExtractorType, Callable[..., RawCommand]] = {
            ExtractorType.PLUGIN: self._perform_plugin_extraction,
            ExtractorType.TEMPLATE: self._perform_template_extraction,
            ExtractorType.PROTOTYPE: self._perform_prototype_extraction,
            ExtractorType.AZURE_CLOUD_EXTRACTOR: partial(
                self._perform_cloud_native_extraction,
                cloud_extractor_type=CloudNativeExtractors.AZURE_CLOUD_EXTRACTOR,
            ),
            ExtractorType.LLM: self._perform_llm_extraction,
        }

        self._logger = logging.getLogger(self.__class__.__name__)

    def make_for(self, extractor_id: str, extractor_type: ExtractorType) -> ExtractionStep:
        step_id = uuid4().hex
        command = self._extraction_commands[extractor_type](extractor_id=extractor_id, step_id=step_id)

        return ExtractionStep(id_=EntityId(step_id), raw_command=command)

    def make_reply_extraction(self) -> ExtractionStep:
        step_id = uuid4().hex
        command = PerformExtractionReply(
            error_type=None,
            error_message=None,
        )
        raw_command: RawCommand = {
            "channel": self._correlation_destination,
            "command": command,
            "reply_to": "NONE",
            "headers": self._correlation_headers | self._make_reply_extraction_headers(command),
        }
        return ExtractionStep(id_=EntityId(step_id), raw_command=raw_command)

    def _perform_plugin_extraction(self, extractor_id: str, step_id: str) -> RawCommand:
        headers = self._prepare_headers(step_id) | self._make_routing_info()

        return {
            "channel": self._command_channel,
            "command": ExtractDocument(
                document_id=self._document_id,
                language=self._language,
                engine=self._engine,
            ),
            "reply_to": self._destination,
            "headers": headers,
        }

    def _perform_llm_extraction(self, extractor_id: str, step_id: str) -> RawCommand:
        return {
            "channel": Destination.AI_FUSION_SERVICE,
            "command": PerformLLMExtraction(
                extractor_id=extractor_id,
                document_id=self._document_id,
                llm_type=self._llm_type,
            ),
            "reply_to": self._destination,
            "headers": self._prepare_headers(step_id),
        }

    def _perform_template_extraction(self, extractor_id: str, step_id: str) -> RawCommand:
        return {
            "channel": Destination.TEMPLATE_SERVICE,
            "command": PerformTemplateExtraction(
                template_id=self._document_type_id,
                tenant_id=self._tenant_id,
                document_id=int(self._document_id),
                version_id=self._template_version_id,
                language=self._language,
                engine=self._engine,
            ),
            "reply_to": self._destination,
            "headers": self._prepare_headers(step_id),
        }

    def _perform_prototype_extraction(self, extractor_id: str, step_id: str) -> RawCommand:
        return {
            "channel": Destination.PROTOTYPE_SERVICE,
            "command": PerformPrototypeExtraction(
                prototype_id=self._document_type_id,
                tenant_id=self._tenant_id,
                document_id=int(self._document_id),
                language=self._language,
                engine=self._engine,
            ),
            "reply_to": self._destination,
            "headers": self._prepare_headers(step_id),
        }

    def _perform_cloud_native_extraction(
        self,
        cloud_extractor_type: CloudNativeExtractors,
        extractor_id: str,
        step_id: str,
    ) -> RawCommand:
        return {
            "channel": Destination.CLOUD_NATIVE_EXTRACTION_SERVICE,
            "command": PerformCloudNativeExtraction(
                document_id=self._document_id,
                extractor_id=self._document_type_id,
                extractor_type=cloud_extractor_type,
            ),
            "reply_to": self._destination,
            "headers": self._prepare_headers(step_id),
        }

    def _get_correlation_destination(self) -> str:
        return self._correlation_headers.get(CommandMessageHeaders.in_reply(CommandMessageHeaders.REPLY_TO))

    def _make_routing_info(self) -> dict[str, Any]:
        return {"routing_info": self._correlation_headers}

    def _make_reply_extraction_headers(self, command: Command) -> dict[str, str]:
        headers = {
            ReplyMessageHeaders.REPLY_TYPE: command.__class__.__name__,
            ReplyMessageHeaders.REPLY_OUTCOME: CommandReplyOutcome.SUCCESS.value,
        }

        if metadata := self._extra_headers.get(CommandMessageHeaders.METADATA):
            headers.update({CommandMessageHeaders.METADATA: metadata})

        return headers

    def _prepare_headers(self, step_id: str) -> dict[str, str]:
        base_headers = self._update_commandreply_to(self._get_command_headers())
        return self._add_extraction_worfklow_info(base_headers=base_headers, step_id=step_id)

    def _get_command_headers(self) -> dict[str, str]:
        return {
            key: value
            for key, value in self._extra_headers.items()
            if key.startswith(CommandMessageHeaders.COMMAND_HEADER_PREFIX)
        }

    def _add_extraction_worfklow_info(self, base_headers: dict[str, str], step_id: str) -> dict[str, str]:
        try:
            metadata = json.loads(self._extra_headers.get(CommandMessageHeaders.METADATA, "{}"))  # noqa: P103
        except json.JSONDecodeError:
            self._logger.warning(
                "Can't decode command metadata: %s",
                self._extra_headers.get(CommandMessageHeaders.METADATA),
            )
            metadata = {}

        metadata.update({"workflow_id": self._workflow_id, "step_id": step_id})

        base_headers[CommandMessageHeaders.METADATA] = json.dumps(metadata)

        return base_headers

    @staticmethod
    def _update_commandreply_to(command_headers: dict[str, Any]) -> dict[str, Any]:
        command_headers[CommandMessageHeaders.REPLY_TO] = COMMANDS_REPLIES_CHANNEL
        return command_headers
