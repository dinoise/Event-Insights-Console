# Models
from models.source import Source

# Schemas
from schemas.source_schema import SourceSchema

class SourceService:

    @staticmethod
    def get_all_sources():
        sources = Source.query.all()
        return SourceSchema(many=True).dump(sources)