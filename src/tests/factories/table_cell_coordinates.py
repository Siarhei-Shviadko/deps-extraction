import factory
from deps_extracted_data.model.extracted_data.data_types import TableCellCoordinates

__all__ = ["TableCellCoordinatesFactory"]


class TableCellCoordinatesFactory(factory.Factory):
    class Meta:
        model = TableCellCoordinates

    column = factory.Faker("pyint", min_value=0)
    row = factory.Faker("pyint", min_value=0)
    column_span = factory.Faker("pyint", min_value=1)
    row_span = factory.Faker("pyint", min_value=1)
