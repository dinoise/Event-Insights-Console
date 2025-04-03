# Flask libraries
from flask import jsonify

# Services
from services.event_mapping_columns_service import EventMappingColumnsService

class EventMappingColumnsController:
    
    @staticmethod
    def get_mapping_columns() -> tuple:
        columns = EventMappingColumnsService.get_all_mapping_columns()
        return jsonify({
            "status": 200,
            "code": "success",
            "data": columns
        }), 200
