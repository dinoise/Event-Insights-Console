# Models
from models.event_type import EventType

# Schemas
from schemas.event_type_schema import EventTypeSchema

# Types
from typing import List, Dict, Any

class EventTypeService:

    @staticmethod
    def get_all_event_types() -> List[Dict[str, Any]]:
        event_types = EventType.query.all()
        return EventTypeSchema(many=True).dump(event_types)