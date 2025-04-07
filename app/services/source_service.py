# Models
from models.source import Source

# Schemas
from schemas.source_schema import SourceSchema

# Types
from typing import List, Dict, Any

class SourceService:

    @staticmethod
    def get_all_sources() -> List[Dict[str, Any]]:
        sources = Source.query.all()
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