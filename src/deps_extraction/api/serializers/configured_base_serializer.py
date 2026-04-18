from pydantic import BaseModel, ConfigDict

__all__ = ["ConfiguredBaseSerializer"]


class ConfiguredBaseSerializer(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        ser_json_smart_union=True,
    )
