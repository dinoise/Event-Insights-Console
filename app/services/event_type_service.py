# Models
from models.event_type import EventType

# Schemas
from schemas.event_type_schema import EventTypeSchema

# Types
from typing import List, Dict, Any

class EventTypeService:

    @staticmethod
    def get_all_event_types() -> List[Dict[str, Any]]:
        event_types = EventType.query.filter_by(
            event_type_status="ACTIVE"
        ).all()

        if not event_types:
            return None
        
        return EventTypeSchema(many=True).dump(event_types)
    
    @staticmethod
    def get_event_type_by_pk(event_type_id: int) -> Dict[str, Any]:
        event_type = EventType.query.filter_by(
            event_type_id=event_type_id,
            event_type_status="ACTIVE"
        ).first()

        if not event_type:
            return None
        
        return EventTypeSchema(many=False).dump(event_type)