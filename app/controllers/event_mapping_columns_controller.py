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
                "message": "Columns not found for this mapping id",
                "data": []
            }), HTTPStatus.NOT_FOUND
        
        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": columns
        }), HTTPStatus.OK
    
    @staticmethod
    def post_mapping_column() -> tuple:
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
    
    @staticmethod
    def bulk_create_mapping_columns() -> tuple[dict, int]:
        if not request.is_json:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "Request must be JSON"
            }), HTTPStatus.BAD_REQUEST
        
        body = request.get_json()
        if not body:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "JSON must not be empty"
            }), HTTPStatus.BAD_REQUEST
        
        required_fields = {
            'event_mapping_id': (int, lambda x: x > 0),
            'mapping_sequence': (int, lambda x: x > 0),
            'mapping_data_type': (str, lambda x: 0 < len(x) <= 150),
            'mapping_nullable': (bool, None),
            'mapping_origin_column': (str, lambda x: 0 < len(x) <= 150),
            'mapping_target_column': (str, lambda x: 0 < len(x) <= 150),
            'mapping_created_by': (str, lambda x: 0 < len(x) <= 150)
        }

        errors = []
        validated_data = []
        
        for idx, column in enumerate(body, start=1):
            try:
                missing_fields = [field for field in required_fields if field not in column]
                if missing_fields:
                    raise ValueError(f"Register {idx}: Missing Values: {', '.join(missing_fields)}")
                
                temp_data = {}
                for field, (field_type, validator) in required_fields.items():
                    if not isinstance(column[field], field_type):
                        raise ValueError(f"Register {idx}: '{field}' must be {field_type.__name__}")
                    
                    if validator and not validator(column[field]):
                        raise ValueError(f"Register {idx}: invalid value for '{field}'")
                    
                    temp_data[field] = column[field]

                # Optional fields
                temp_data['mapping_validation_regex'] = column.get('mapping_validation_regex')
                temp_data['mapping_target_label'] = column.get('mapping_target_label')

                validated_data.append(temp_data)
            except ValueError as ve:
                errors.append(str(ve))

        if errors:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "error",
                "message": "Errors detected, see the node 'errors' for details",
                "errors": errors
            }), HTTPStatus.BAD_REQUEST

        try:
            results = EventMappingColumnsService.bulk_create_mapping_columns(validated_data)
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        return jsonify({
            "status": HTTPStatus.CREATED,
            "code": "success",
            "data": results
        }), HTTPStatus.CREATED
    
    @staticmethod
    def update_mapping_column(mapping_column_id: int) -> tuple[dict, int]:
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
            'mapping_sequence': (int, lambda x: x > 0),
            'mapping_data_type': (str, lambda x: 0 < len(x) <= 150),
            'mapping_nullable': (bool, None),
            'mapping_validation_regex': (str, lambda x: len(x) <= 250 if x else True),
            'mapping_origin_column': (str, lambda x: 0 < len(x) <= 150),
            'mapping_target_column': (str, lambda x: 0 < len(x) <= 150),
            'mapping_target_label': (str, lambda x: len(x) <= 150 if x else True)
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
            updated_column = EventMappingColumnsService.update_mapping_column(
                mapping_column_id=mapping_column_id,
                update_data=update_data
            )
        except Exception as e:
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": f"Internal server error: {str(e)}"
            }), HTTPStatus.INTERNAL_SERVER_ERROR

        if not updated_column:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "success",
                "message": "No mapping column for that mapping_column_id",
                "data": updated_column
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": updated_column
        }), HTTPStatus.OK