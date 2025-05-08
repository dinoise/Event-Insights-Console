from __init__ import db
from pgvector.sqlalchemy import VECTOR

class EventEmbedding(db.Model):
    """Model for the table tb_lvp_event_embeddings"""
    __bind_key__ = 'postgres'
    __tablename__ = 'tb_lvp_event_embeddings'
    
    event_uuid = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False
    )
    target_dataset = db.Column(db.String(200), nullable=False)
    target_table = db.Column(db.String(250), nullable=False)
    embedding_event_message = db.Column(db.Text, nullable=False)
    embedding_embedded_message = db.Column(VECTOR(768), nullable=False) 
    embedding_timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)