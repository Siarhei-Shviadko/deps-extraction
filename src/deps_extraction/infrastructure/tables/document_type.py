from sqlalchemy import Column, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from deps_extraction.extras.datasource import metadata

__all__ = ["document_type_table"]

document_type_table = Table(
    "document_type",
    metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("extraction_type", String, nullable=True),
    Column("extractors", JSONB, nullable=False),
    UniqueConstraint("id", "tenant_id", name="id_tenant_id_uc"),
)
