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