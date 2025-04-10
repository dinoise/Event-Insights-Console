from __init__ import db

class EventType(db.Model):
    """Model for the table tb_lvp_event_type"""
    __tablename__ = 'tb_lvp_event_type'
    
    event_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_domain = db.Column(db.String(50))
    event_stage = db.Column(db.String(30))
    event_type_name = db.Column(db.String(50))
    event_type_description = db.Column(db.String(100))
    event_type_action = db.Column(db.String(100))
    event_type_story_message = db.Column(db.String(250))
    event_type_status = db.Column(db.String(30))
    event_payload_file_target = db.Column(db.String(250))
    event_type_pubsub_topic_name = db.Column(db.String(300))
    event_type_version = db.Column(db.Float)
    event_documentation_link = db.Column(db.String(350))
    event_type_created_on = db.Column(db.TIMESTAMP)
    event_type_created_by = db.Column(db.String(100))

    # def __repr__(self):
    #     return f"Event of id {self.event_type_id} is the type {self.event_type_name}. The action of this event is {self.event_type_action}"