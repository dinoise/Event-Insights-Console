# Models
from models.event_mapping import EventMapping

# Schemas
from schemas.event_mapping_schema import EventMappingSchema

# Types
from typing import List, Dict, Any

from __init__ import db

class EventMappingService:

    @staticmethod
    def get_all_event_mappings() -> List[Dict[str, Any]]:
        mappings = EventMapping.query.all()
        return EventMappingSchema(many=True).dump(mappings)
    
    @staticmethod
    def create_mapping(event_type_id: int, source_id: int, event_mapping_description: str, 
                       event_mapping_version: float, event_mapping_target_dataset: str, event_mapping_target_table: str) -> int:
        new_mapping = EventMapping(
            event_type_id=event_type_id,
            source_id=source_id,
            event_mapping_description=event_mapping_description,
            event_mapping_version=event_mapping_version,
            event_mapping_target_dataset=event_mapping_target_dataset,
            event_mapping_target_table=event_mapping_target_table,
            event_mapping_status="ACTIVE",
            event_mapping_created_by="system"
        )
        db.session.add(new_mapping)
        db.session.commit()

        return new_mapping.event_mapping_id  