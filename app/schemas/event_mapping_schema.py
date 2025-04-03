from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.event_mapping import EventMapping 

class EventMappingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventMapping
        exclude = ('event_mapping_status', 'event_mapping_created_by', 'event_mapping_created_on')  # exclude this fileds