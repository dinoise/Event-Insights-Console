from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.source import Source

class SourceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Source
        fields = ('source_id', 'source_description')  # return only this fileds