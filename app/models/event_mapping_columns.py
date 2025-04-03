from __init__ import db

class EventMappingColumns(db.Model):
    """Model for the table tb_lvp_event_mapping_columns"""
    __tablename__ = 'tb_lvp_event_mapping_columns'
    
    mapping_column_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_mapping_id = db.Column(db.Integer, nullable=False)
    mapping_sequence = db.Column(db.Integer, nullable=False)
    mapping_data_type = db.Column(db.String(150), nullable=False)
    mapping_nullable = db.Column(db.Boolean, nullable=False)
    mapping_validation_regex = db.Column(db.String(250), nullable=True)
    mapping_origin_column = db.Column(db.String(150), nullable=False)
    mapping_target_column = db.Column(db.String(150), nullable=False)
    mapping_target_label = db.Column(db.String(150), nullable=True)
    mapping_target_status = db.Column(db.String(150), nullable=False)
    mapping_created_by = db.Column(db.String(150), nullable=False)
    mapping_created_on = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)