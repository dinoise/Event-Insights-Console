# Models
from models.event_type import EventType

# Schemas
from schemas.event_type_schema import EventTypeSchema

# Types
from typing import List, Dict, Any

from __init__ import db

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
    
    @staticmethod
    def update_event_type(event_type_id: int, update_data: Dict) -> List[Dict[str, Any]]:
        try:
            event_type = EventType.query.filter_by(
                event_type_id=event_type_id,
                event_type_status="ACTIVE"
            ).first()
            if not event_type:
                return []

            for field, value in update_data.items():
                setattr(event_type, field, value)
            
            db.session.commit()

            return EventTypeSchema(many=False).dump(event_type)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")