from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.source import Source

class SourceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Source
        exclude = ('source_status', 'source_created_by')  # exlude this fileds