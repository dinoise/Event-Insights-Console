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
    def create_event_type(
        event_type_name: int,
        event_type_description: int,
        event_type_action: str,
        event_domain: bool,
        event_stage: str,
        event_type_version: float,
        event_type_story_message: str = None,
        event_type_pubsub_topic_name: str = None,
        event_documentation_link: str = None
    ) -> Dict:
        new_event_type = EventType(
            event_type_name=event_type_name,
            event_type_description=event_type_description,
            event_type_action=event_type_action,
            event_domain=event_domain,
            event_stage=event_stage,
            event_type_version=event_type_version,
            event_type_story_message=event_type_story_message,
            event_type_pubsub_topic_name=event_type_pubsub_topic_name,
            event_documentation_link=event_documentation_link,
            event_type_status="ACTIVE",
            event_type_created_by="system"
        )
        
        try:
            db.session.add(new_event_type)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        
        return EventTypeSchema(many=False).dump(new_event_type)
    
    @staticmethod
    def update_event_type(event_type_id: int, update_data: Dict) -> Dict[str, Any]:
        try:
            event_type = EventType.query.filter_by(
                event_type_id=event_type_id,
                event_type_status="ACTIVE"
            ).first()
            if not event_type:
                return {}

            for field, value in update_data.items():
                setattr(event_type, field, value)
            
            db.session.commit()

            return EventTypeSchema(many=False).dump(event_type)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        
    @staticmethod
    def delete_event_type(event_type_id: int) -> Dict[str, Any]:
        try:
            event_type = EventType.query.filter_by(
                event_type_id=event_type_id,
                event_type_status="ACTIVE"
            ).first()
            if not event_type:
                return {}

            setattr(event_type, "event_type_status", "INACTIVE")
            
            db.session.commit()

            return EventTypeSchema(many=False).dump(event_type)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")