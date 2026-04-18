import importlib
from dataclasses import asdict
from typing import Any

from deps_message_flow.commands.common import Command

from deps_extraction.domain.model import (
    EntityId,
    ErrorType,
    ExtractionStep,
    ExtractionStepError,
    StepStatus,
)
from deps_extraction.domain.types import RawCommand

__all__ = ["ExtractionStepMapper"]


def _import_class(full_class_path: str) -> Command:
    module_name, class_name = full_class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class ExtractionStepMapper:
    @classmethod
    def to_dict(cls, step: ExtractionStep) -> dict[str, Any]:
        return {
            "id": step.id(),
            "raw_command": CommandMapper.to_dict(step.raw_command),
            "status": step.status,
            "error": ErrorMapper.to_dict(step.error) if step.error else None,
        }

    @classmethod
    def from_raw(cls, raw_step: dict[str, Any]) -> ExtractionStep:
        return ExtractionStep(
            id_=EntityId(raw_step["id"]),
            raw_command=CommandMapper.from_raw(raw_step["raw_command"]),
            status=StepStatus(raw_step["status"]),
            error=ErrorMapper.from_raw(raw_step["error"]) if raw_step["error"] else None,
        )


class CommandMapper:
    @classmethod
    def to_dict(cls, command: RawCommand) -> dict[str, Any]:
        return {
            "channel": command["channel"],
            "command": {
                "command_class_name": (
                    f"{command['command'].__class__.__module__}." f"{command['command'].__class__.__name__}"
                ),
                "command_payload": asdict(command["command"]),
            },
            "reply_to": command["reply_to"],
            "headers": command["headers"],
        }

    @classmethod
    def from_raw(cls, raw_data: dict[str, Any]) -> RawCommand:
        return {
            "channel": raw_data["channel"],
            "reply_to": raw_data["reply_to"],
            "headers": raw_data["headers"],
            "command": _import_class(raw_data["command"]["command_class_name"])(
                **raw_data["command"]["command_payload"],
            ),
        }


class ErrorMapper:
    @classmethod
    def to_dict(cls, error: ExtractionStepError) -> dict[str, str]:
        return {
            "error_type": error.error_type,
            "error_message": error.error_message,
        }

    @classmethod
    def from_raw(cls, raw_data: dict[str, str]) -> ExtractionStepError:
        return ExtractionStepError(
            error_type=ErrorType(raw_data["error_type"]),
            error_message=raw_data["error_message"],
        )
