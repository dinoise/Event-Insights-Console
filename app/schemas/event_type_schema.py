from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.event_type import EventType

class EventTypeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventType
        exclude = ('event_type_status', 'event_type_created_on', 'event_type_created_by')  # exclude this fileds