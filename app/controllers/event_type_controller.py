# Flask libraries
from flask import jsonify

# Services
from services.event_type_service import EventTypeService

class EventTypeController:
    
    @staticmethod
    def get_event_types() -> tuple:
        event_types = EventTypeService.get_all_event_types()
        if not event_types:
            return jsonify({
                "status": 404,
                "code": "error",
                "data": []
            }), 404
        
        return jsonify({
            "status": 200,
            "code": "success",
            "data": event_types
        }), 200
