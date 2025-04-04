from flask import Blueprint
from controllers.event_mapping_columns_controller import EventMappingColumnsController

bp = Blueprint('mapping_columns', __name__, url_prefix='/api/mapping-columns')

@bp.route('/<int:mapping_id>', methods=['GET'])
def get_mapping_columns(mapping_id):
    return EventMappingColumnsController.get_mapping_columns(mapping_id)

@bp.route('', methods=['POST'])
def post_mapping_columns():
    return EventMappingColumnsController.post_mapping_column()

@bp.route('/bulk', methods=['POST'])
def post_mapping_columns_bulk():
    return EventMappingColumnsController.bulk_create_mapping_columns()

@bp.route('/<int:mapping_id>', methods=['PUT'])
def update_mapping_column(mapping_id):
    return EventMappingColumnsController.update_mapping_column(mapping_id)

@bp.route('/<int:mapping_id>', methods=['DELETE'])
def delete_mapping_column(mapping_id):
    return EventMappingColumnsController.delete_mapping_column(mapping_id)