from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from deps_extraction.domain.interfaces import IExtractionWorkflowRepository
from deps_extraction.domain.model import ExtractionWorkflow
from deps_extraction.extras.datasource import Database

from ...tables import workflow_table
from .mappers import ExtractionWorkflowMapper

__all__ = ["ExtractionWorkflowRepository"]


class ExtractionWorkflowRepository(IExtractionWorkflowRepository):
    def __init__(self, database: Database):
        self._db = database

    def get(self, id_: str) -> Optional[ExtractionWorkflow]:
        query = select([workflow_table]).where(workflow_table.c.id == id_)
        with self._db.connection() as conn:
            result = conn.execute(query).fetchone()

        return ExtractionWorkflowMapper.from_raw(result) if result else None

    def save(self, workflow: ExtractionWorkflow) -> None:
        raw_workflow = ExtractionWorkflowMapper.to_dict(workflow)
        query = (
            insert(workflow_table)
            .values(**raw_workflow)
            .on_conflict_do_update(
                index_elements=[workflow_table.c.id],
                set_={
                    column.name: getattr(insert(workflow_table).excluded, column.name)
                    for column in workflow_table.columns
                    if column.name != "id"
                },
            )
        )
        with self._db.connection() as conn:
            conn.execute(query)
