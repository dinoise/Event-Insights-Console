from __init__ import db

class EventMapping(db.Model):
    """Model for the table tb_lvp_event_mapping"""
    __tablename__ = 'tb_lvp_event_mapping'
    
    event_mapping_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type_id = db.Column(db.Integer, nullable=True)
    source_id = db.Column(db.Integer, nullable=True)
    event_mapping_description = db.Column(db.String(200), nullable=True)
    event_mapping_version = db.Column(db.Numeric(3, 1), nullable=True) 
    event_mapping_target_dataset = db.Column(db.String(200), nullable=True)
    event_mapping_target_table = db.Column(db.String(250), nullable=True)
    event_mapping_status = db.Column(db.String(55), nullable=True)
    event_mapping_created_by = db.Column(db.String(200), nullable=True)
    event_mapping_created_on = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())