from sqlalchemy import Column, Float, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_extraction.extras.datasource import metadata

__all__ = ["extracted_field_table"]

extracted_field_table = Table(
    "extracted_field",
    metadata,
    Column("id", String),
    Column("document_id", Integer, primary_key=True),
    Column("field_code", String, primary_key=True),
    Column("index", String, primary_key=True),
    Column("value", String),
    Column("field_type", String),
    Column("meta", JSONB),
    Column("confidence", Float),
    Column("source_bbox_coordinates", JSONB),
    Column("source_table_coordinates", JSONB),
    Column("source_text_coordinates", JSONB),
    Column("table_cell_coordinates", JSONB),
)
