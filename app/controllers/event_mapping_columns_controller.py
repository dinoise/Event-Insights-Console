# Flask libraries
from flask import jsonify

# Services
from services.event_mapping_columns_service import EventMappingColumnsService

class EventMappingColumnsController:
    
    @staticmethod
    def get_mapping_columns(mapping_id: int) -> tuple:
        columns = EventMappingColumnsService.get_all_mapping_columns(mapping_id)
        if not columns:
            return jsonify({
                "status": 404,
                "code": "error",
                "data": []
            }), 404
        
        return jsonify({
            "status": 200,
            "code": "success",
            "data": columns
        }), 200
