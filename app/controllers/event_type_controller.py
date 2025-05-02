# Flask libraries
from flask import jsonify, request

# Services
from services.event_type_service import EventTypeService

from http import HTTPStatus

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
    
    @staticmethod
    def post_event_mapping() -> tuple:
        body = request.get_json()

        required_params = [
            "event_type_name",
            "event_type_description",
            "event_type_action",
            "event_domain",
            "event_stage",
            "event_type_version"
        ]

        missing_params = [param for param in required_params if param not in body or body[param] is None]
        if missing_params:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": f"Missing required parameters: {', '.join(missing_params)}"
            }), HTTPStatus.BAD_REQUEST

        try:
            new_event_type = EventTypeService.create_event_type(event_type_name=body['event_type_name'],
                                                                event_type_description=body['event_type_description'],
                                                                event_type_action=body['event_type_action'],
                                                                event_domain=body['event_domain'],
                                                                event_stage=body['event_stage'],
                                                                event_type_version=body['event_type_version'],
                                                                event_type_story_message=body.get('event_type_story_message'),
                                                                event_type_pubsub_topic_name=body.get('event_type_pubsub_topic_name'),
                                                                event_documentation_link=body.get('event_documentation_link'))
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
                "new_event_type": new_event_type,
                "message": "Mapping created successfully"
            }
        }), HTTPStatus.CREATED
    
    @staticmethod
    def update_event_type(event_type_id: int) -> tuple:
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
            'event_type_name':(str, lambda x: 0 < len(x) <= 150),
            'event_type_description': (str, lambda x: 0 < len(x) <= 150),
            'event_type_action': (str, lambda x: 0 < len(x) <= 150),
            'event_type_story_message': (str, lambda x: 0 < len(x) <= 1000),
            'event_type_pubsub_topic_name': (str, lambda x: 0 < len(x) <= 150),
            'event_documentation_link': (str, lambda x: 0 < len(x) <= 150),
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
            updated_type = EventTypeService.update_event_type(
                event_type_id=event_type_id,
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
    def delete_event_type(event_type_id) -> tuple:
        try:
            deleted_mapping = EventTypeService.delete_event_type(
                event_type_id=event_type_id
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
                "message": "Mapping not found"
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success"
        }), HTTPStatus.OK