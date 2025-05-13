from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.event_embeddings import EventEmbedding
from utils.utils import VectorField

class EventEmbeddingSchema(SQLAlchemyAutoSchema):
    embedding_embedded_message = VectorField()

    class Meta:
        model = EventEmbedding
        exclude = ('embedding_embedded_message', 'embedding_event_message')  # exclude this field