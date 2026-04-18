from sqlalchemy import Column, Integer, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_extraction.extras.datasource import metadata

__all__ = ["groups_table"]

groups_table = Table(
    "groups",
    metadata,
    Column("document_id", Integer, primary_key=True),
    Column("groups", JSONB),
)
