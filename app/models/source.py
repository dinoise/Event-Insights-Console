from __init__ import db

class Source(db.Model):
    """Model for the table tb_lvp_cat_sources"""
    __tablename__ = 'tb_lvp_cat_sources'
    
    source_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_name = db.Column(db.String(100), nullable=True)
    source_description = db.Column(db.String(255), nullable=True)
    source_status = db.Column(db.String(100), nullable=True)
    source_created_by = db.Column(db.String(100), nullable=True)
