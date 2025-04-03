# Flask libraries
from flask import jsonify

# Services
from services.event_mapping_service import EventMappingService

class EventMappingController:
    
    @staticmethod
    def get_event_mappings() -> tuple:
        mappings = EventMappingService.get_all_event_mappings()
        if not mappings:
            return jsonify({
                "status": 404,
                "code": "error",
                "data": []
            }), 404
        
        return jsonify({
            "status": 200,
            "code": "success",
            "data": mappings
        }), 200
