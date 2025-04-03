# Models
from models.event_type import EventType

# Schemas
from schemas.event_type_schemal import EventTypeSchema

class EventTypeService:

    @staticmethod
    def get_all_event_types():
        event_types = EventType.query.all()
        return EventTypeSchema(many=True).dump(event_types)