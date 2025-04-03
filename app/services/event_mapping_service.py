# Models
from models.event_mapping import EventMapping

# Schemas
from schemas.event_mapping_schema import EventMappingSchema

class EventMappingService:

    @staticmethod
    def get_all_event_mappings():
        mappings = EventMapping.query.all()
        return EventMappingSchema(many=True).dump(mappings)