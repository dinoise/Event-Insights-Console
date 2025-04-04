# Flask libraries
from flask import jsonify, request

# Services
from services.event_mapping_columns_service import EventMappingColumnsService

from http import HTTPStatus

class EventMappingColumnsController:
    
    @staticmethod
    def get_mapping_columns(mapping_id: int) -> tuple:
        columns = EventMappingColumnsService.get_all_mapping_columns(mapping_id)
        if not columns:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "error",
                "data": []
            }), HTTPStatus.NOT_FOUND
        
        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": columns
        }), HTTPStatus.OK
    
    @staticmethod
    def post_mapping_columns() -> tuple:
        if not request.is_json:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "Request must be JSON"
            }), HTTPStatus.BAD_REQUEST
        
        body = request.get_json()

        required_fields = [
            'event_mapping_id',
            'mapping_sequence',
            'mapping_data_type',
            'mapping_nullable',
            'mapping_origin_column',
            'mapping_target_column'
        ]

        # Verificar campos faltantes
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), HTTPStatus.BAD_REQUEST

        try:
            new_column_id = EventMappingColumnsService.create_mapping_column(
                    event_mapping_id=body['event_mapping_id'],
                    mapping_sequence=body['mapping_sequence'],
                    mapping_data_type=body['mapping_data_type'],
                    mapping_nullable=body['mapping_nullable'],
                    mapping_origin_column=body['mapping_origin_column'],
                    mapping_target_column=body['mapping_target_column'],
                    mapping_validation_regex=body.get('mapping_validation_regex'),
                    mapping_target_label=body.get('mapping_target_label')
                )
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    
        return jsonify({
            "status": HTTPStatus.CREATED,
            "code": "success",
            "data": {
                "mapping_column_id": new_column_id,
                "message": "Column mapping created successfully"
            }
        }), HTTPStatus.CREATED