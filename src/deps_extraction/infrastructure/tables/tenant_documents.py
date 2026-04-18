from sqlalchemy import Column, Integer, String, Table, UniqueConstraint

from deps_extraction.extras.datasource import metadata

__all__ = ["tenant_documents_table"]

tenant_documents_table = Table(
    "tenant_documents",
    metadata,
    Column("tenant_id", String),
    Column("document_id", Integer),
    UniqueConstraint("document_id", "tenant_id", name="unique_tenant_id_document_id"),
)
