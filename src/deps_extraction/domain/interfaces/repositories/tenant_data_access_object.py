from abc import ABC, abstractmethod

from sqlalchemy.engine.base import Connection

from deps_extraction.domain.dtos import ExtractedDataListFilterObject

__all__ = ["ITenantDAO"]


class ITenantDAO(ABC):
    @abstractmethod
    def add_to_tenant(self, conn: Connection, document_id: int) -> None:
        pass

    @abstractmethod
    def remove_from_tenant(self, conn: Connection, document_id: int) -> None:
        pass

    @abstractmethod
    def get_document_ids(self, conn: Connection) -> list[int]:  # noqa: WPS463
        pass

    @abstractmethod
    def check_access(self, conn: Connection, document_id: int) -> None:
        pass

    @abstractmethod
    def patch_filter(self, conn: Connection, filtering: ExtractedDataListFilterObject) -> None:
        pass
