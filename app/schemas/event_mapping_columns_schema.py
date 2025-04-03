from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.event_mapping_columns import EventMappingColumns

class EventMappingColumnsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventMappingColumns
        exclude = ('mapping_target_status', 'mapping_created_by', 'mapping_created_on')  # exclude this fileds