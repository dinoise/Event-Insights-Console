# Models
from models.event_mapping_columns import EventMappingColumns

# Schemas
from schemas.event_mapping_columns_schema import EventMappingColumnsSchema

# Types
from typing import List, Dict, Any

class EventMappingColumnsService:

    @staticmethod
    def get_all_mapping_columns(mapping_id) -> List[Dict[str, Any]]:
        columns = EventMappingColumns.query.filter_by(
            event_mapping_id=mapping_id,
            mapping_target_status="ACTIVE"
        ).order_by(
            EventMappingColumns.mapping_sequence.asc()
        ).all()

        return EventMappingColumnsSchema(many=True).dump(columns)