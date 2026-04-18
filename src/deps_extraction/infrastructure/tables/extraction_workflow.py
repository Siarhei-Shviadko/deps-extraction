from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_extraction.extras.datasource import metadata

__all__ = ["workflow_table"]


workflow_table = Table(
    "extraction_workflow",
    metadata,
    Column("id", String, primary_key=True),
    Column("document_id", String, nullable=False),
    Column("steps", JSONB, nullable=False),
    Column("current_step_index", Integer, nullable=False),
)
