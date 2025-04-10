# Models
from models.source import Source

# Schemas
from schemas.source_schema import SourceSchema

# Types
from typing import List, Dict, Any

from __init__ import db

class SourceService:

    @staticmethod
    def get_all_sources() -> List[Dict[str, Any]]:
        sources = Source.query.filter_by(
            source_status="ACTIVE"
        ).all()

        if not sources:
            return None

        return SourceSchema(many=True).dump(sources)
    
    @staticmethod
    def get_source_by_pk(source_id: int) -> Dict[str, Any]:
        source = Source.query.filter_by(
            source_id=source_id,
            source_status="ACTIVE"
        ).first()

        if not source:
            return None
        
        return SourceSchema(many=False).dump(source)
    
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
    def create_source(
        source_name: str,
        source_description: str
    ) -> Dict:
        new_source = Source(
            source_name=source_name,
            source_description=source_description,
            source_status="ACTIVE",
            source_created_by="system"
        )
        
        try:
            db.session.add(new_source)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        
        return SourceSchema(many=False).dump(new_source)
    
    @staticmethod
    def update_source(source_id: int, update_data: Dict) -> Dict[str, Any]:
        try:
            source = Source.query.filter_by(
                source_id=source_id,
                source_status="ACTIVE"
            ).first()
            if not source:
                return {}

            for field, value in update_data.items():
                setattr(source, field, value)
            
            db.session.commit()

            return SourceSchema(many=False).dump(source)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        

    @staticmethod
    def delete_source(source_id: int) -> Dict[str, Any]:
        try:
            source = Source.query.filter_by(
                source_id=source_id,
                source_status="ACTIVE"
            ).first()
            if not source:
                return {}

            setattr(source, "source_status", "INACTIVE")
            
            db.session.commit()

            return SourceSchema(many=False).dump(source)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")