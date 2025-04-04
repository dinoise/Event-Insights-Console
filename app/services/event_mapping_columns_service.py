# Models
from models.event_mapping_columns import EventMappingColumns

# Schemas
from schemas.event_mapping_columns_schema import EventMappingColumnsSchema

# Types
from typing import List, Dict, Any

from __init__ import db

class EventMappingColumnsService:

    @staticmethod
    def get_all_mapping_column(mapping_id) -> List[Dict[str, Any]]:
        columns = EventMappingColumns.query.filter_by(
            event_mapping_id=mapping_id,
            mapping_target_status="ACTIVE"
        ).order_by(
            EventMappingColumns.mapping_sequence.asc()
        ).all()

        return EventMappingColumnsSchema(many=True).dump(columns)
    
    @staticmethod
    def create_mapping_column(
        event_mapping_id: int,
        mapping_sequence: int,
        mapping_data_type: str,
        mapping_nullable: bool,
        mapping_origin_column: str,
        mapping_target_column: str,
        mapping_validation_regex: str = None,
        mapping_target_label: str = None
    ) -> int:
        new_column = EventMappingColumns(
            event_mapping_id=event_mapping_id,
            mapping_sequence=mapping_sequence,
            mapping_data_type=mapping_data_type,
            mapping_nullable=mapping_nullable,
            mapping_validation_regex=mapping_validation_regex,
            mapping_origin_column=mapping_origin_column,
            mapping_target_column=mapping_target_column,
            mapping_target_label=mapping_target_label,
            mapping_target_status="ACTIVE",
            mapping_created_by="system"
        )
        
        try:
            db.session.add(new_column)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
        
        return new_column.mapping_column_id
