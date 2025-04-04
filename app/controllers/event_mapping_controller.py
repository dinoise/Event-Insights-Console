# Flask libraries
from flask import jsonify, request

# Services
from services.event_mapping_service import EventMappingService

from http import HTTPStatus

class EventMappingController:
    
    @staticmethod
    def get_event_mappings() -> tuple:
        mappings = EventMappingService.get_all_event_mappings()
        if not mappings:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "data": []
            }), HTTPStatus.BAD_REQUEST
        
        return jsonify({
            "status": HTTPStatus.FOUND,
            "code": "success",
            "data": mappings
        }), HTTPStatus.FOUND
    
    @staticmethod
    def post_event_mappings() -> tuple:
        body = request.get_json()

        required_params = [
            "event_type_id",
            "source_id",
            "event_mapping_description",
            "event_mapping_version",
            "event_mapping_target_dataset",
            "event_mapping_target_table"
        ]

        missing_params = [param for param in required_params if param not in body or body[param] is None]
        if missing_params:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": f"Missing required parameters: {', '.join(missing_params)}"
            }), HTTPStatus.BAD_REQUEST

        try:
            event_type_id = int(body["event_type_id"])
            source_id = int(body["source_id"])
            event_mapping_version = float(body["event_mapping_version"])
        except (ValueError, TypeError):
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "Invalid parameter types: event_type_id and source_id should be integers, event_mapping_version should be a number"
            }), HTTPStatus.BAD_REQUEST

        event_mapping_description = body["event_mapping_description"]
        event_mapping_target_dataset = body["event_mapping_target_dataset"]
        event_mapping_target_table = body["event_mapping_target_table"]

        try:
            new_mapping_id = EventMappingService.create_mapping(event_type_id=event_type_id,
                                                                source_id=source_id,
                                                                event_mapping_description=event_mapping_description,
                                                                event_mapping_version=event_mapping_version,
                                                                event_mapping_target_dataset=event_mapping_target_dataset,
                                                                event_mapping_target_table=event_mapping_target_table)
        except Exception as e:
            error_msg = f"Error creating a new mapping: {str(e)}"
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": error_msg
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        return jsonify({
            "status": HTTPStatus.CREATED,
            "code": "success",
            "data": f"New mapping created: {new_mapping_id}"
        }), HTTPStatus.CREATED
