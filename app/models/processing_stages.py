from __init__ import db

class ProcessingStages(db.Model):
    """Model for the table tb_lvp_cat_processing_stages"""
    __tablename__ = 'tb_lvp_cat_processing_stages'
    
    processing_stage_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    processing_stage_description = db.Column(db.String(250), nullable=True)
    processing_stage_sequence = db.Column(db.Integer, nullable=True)
    processing_stage_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    processing_stage_created_by = db.Column(db.String(100), nullable=True)