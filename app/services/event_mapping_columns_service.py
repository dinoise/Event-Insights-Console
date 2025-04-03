# Models
from models.event_mapping_columns import EventMappingColumns

# Schemas
from schemas.event_mapping_columns_schema import EventMappingColumnsSchema

class EventMappingColumnsService:

    @staticmethod
    def get_all_mapping_columns():
        columns = EventMappingColumns.query.all()
        return EventMappingColumnsSchema(many=True).dump(columns)