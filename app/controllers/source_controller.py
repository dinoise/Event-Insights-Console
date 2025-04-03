# Flask libraries
from flask import jsonify

# Services
from services.source_service import SourceService

class SourceController:
    
    @staticmethod
    def get_sources() -> tuple:
        sources = SourceService.get_all_sources()
        if not sources:
            return jsonify({
                "status": 404,
                "code": "error",
                "data": []
            }), 404
        
        return jsonify({
            "status": 200,
            "code": "success",
            "data": sources
        }), 200
