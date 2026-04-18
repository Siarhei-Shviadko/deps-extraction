from typing import Any, Optional, TypedDict

from deps_message_flow.commands.common import Command

__all__ = ["RawCommand", "RawCommandReply"]


class RawCommand(TypedDict):
    channel: str
    command: Command
    reply_to: str
    headers: dict[str, Any]


class RawCommandReply(TypedDict):
    workflow_id: str
    step_id: str
    error: Optional[str]
    error_message: Optional[str]
