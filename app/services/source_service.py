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