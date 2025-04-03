# Models
from models.event_mapping import EventMapping

# Schemas
from schemas.event_mapping_schema import EventMappingSchema

# Types
from typing import List, Dict, Any

class EventMappingService:

    @staticmethod
    def get_all_event_mappings() -> List[Dict[str, Any]]:
        mappings = EventMapping.query.all()
        return EventMappingSchema(many=True).dump(mappings)