from flask import Blueprint
from controllers.event_mapping_columns_controller import EventMappingColumnsController

bp = Blueprint('mapping_columns', __name__, url_prefix='/api/mapping-columns')

@bp.route('', methods=['GET'])
def get_mapping_columns():
    return EventMappingColumnsController.get_mapping_columns()
