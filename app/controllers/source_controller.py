# Flask libraries
from flask import jsonify, request

# Services
from services.source_service import SourceService

from http import HTTPStatus

class SourceController:
    
    @staticmethod
    def get_sources() -> tuple:
        sources = SourceService.get_all_sources()
        if not sources:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "error",
                "data": []
            }), HTTPStatus.NOT_FOUND
        
        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": sources
        }), HTTPStatus.OK

    @staticmethod
    def post_source() -> tuple:
        body = request.get_json()

        required_params = [
            "source_name",
            "source_description",
        ]

        missing_params = [param for param in required_params if param not in body or body[param] is None]
        if missing_params:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": f"Missing required parameters: {', '.join(missing_params)}"
            }), HTTPStatus.BAD_REQUEST

        try:
            new_source = SourceService.create_source(source_name=body['source_name'], 
                                                         source_description=body['source_description'])
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
                "new_source": new_source,
                "message": "Mapping created successfully"
            }
        }), HTTPStatus.CREATED
    
    @staticmethod
    def update_source(source_id: int) -> tuple:
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
            'source_name':(str, lambda x: 0 < len(x) <= 100),
            'source_description': (str, lambda x: 0 < len(x) <= 255)
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
            updated_type = SourceService.update_source(
                source_id=source_id,
                update_data=update_data
            )
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        if not updated_type:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "success",
                "message": "Mapping not found",
                "data": updated_type
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": updated_type
        }), HTTPStatus.OK
    
    @staticmethod
    def delete_source(source_id) -> tuple:
        try:
            deleted_mapping = SourceService.delete_source(
                source_id=source_id
            )
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        if not deleted_mapping:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "success",
                "message": "Source not found"
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success"
        }), HTTPStatus.OK