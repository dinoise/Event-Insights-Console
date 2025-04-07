# Flask libraries
from flask import jsonify, request

# Services
from services.event_mapping_service import EventMappingService

from http import HTTPStatus

class EventMappingController:
    
    @staticmethod
    def get_event_mapping() -> tuple:
        mappings = EventMappingService.get_all_event_mappings()
        if not mappings:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "data": []
            }), HTTPStatus.BAD_REQUEST
        
        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": mappings
        }), HTTPStatus.OK
    
    @staticmethod
    def post_event_mapping() -> tuple:
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
            "data": {
                "event_mapping_id": new_mapping_id,
                "message": "Mapping created successfully"
            }
        }), HTTPStatus.CREATED

    @staticmethod
    def update_event_mapping(mapping_id) -> tuple:
        if not request.is_json:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "invalid_request",
                "message": "Request must be JSON",
                "data": None
            }), HTTPStatus.BAD_REQUEST

        update_data = request.get_json()

        if not update_data:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "JSON must not be empty"
            }), HTTPStatus.BAD_REQUEST

        allowed_fields = {
            'event_mapping_description':(str, lambda x: 0 < len(x) <= 150),
            'event_mapping_target_dataset': (str, lambda x: 0 < len(x) <= 150),
            'event_mapping_target_table': (str, lambda x: 0 < len(x) <= 150),
            'event_type_id': (int, lambda x: x > 0),
            'source_id': (int, lambda x: x > 0)
        }

        invalid_fields = [field for field in update_data if field not in allowed_fields]
        if invalid_fields:        
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": f"Invalid fields for update: {', '.join(invalid_fields)}"
            }), HTTPStatus.BAD_REQUEST

        validation_errors = []
        for field, value in update_data.items():
            field_type, validator = allowed_fields[field]
            if not isinstance(value, field_type):
                validation_errors.append(f"'{field}' must be {field_type.__name__}")
            elif validator and not validator(value):
                validation_errors.append(f"Invalid value for '{field}'")

        if validation_errors:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "Errors detected, see the node 'errors' for details",
                "errors": validation_errors
            }), HTTPStatus.BAD_REQUEST

        try:
            updated_mapping = EventMappingService.update_mapping(
                mapping_id=mapping_id,
                update_data=update_data
            )
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        if not updated_mapping:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "success",
                "message": "Mapping not found",
                "data": updated_mapping
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": updated_mapping
        }), HTTPStatus.OK
    
    @staticmethod
    def delete_event_mapping(mapping_id) -> tuple:
        try:
            deleted_mapping = EventMappingService.delete_mapping(
                mapping_id=mapping_id
            )
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        print(deleted_mapping)
        if not deleted_mapping:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "success",
                "message": "Mapping not found"
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success"
        }), HTTPStatus.OK
