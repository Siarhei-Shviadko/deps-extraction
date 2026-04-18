from dataclasses import dataclass
from typing import Optional

__all__ = ["AttachmentInfo"]


@dataclass
class AttachmentInfo:
    command_channel: Optional[str]
    document_type_id: str
    extractor_id: Optional[str] = None
