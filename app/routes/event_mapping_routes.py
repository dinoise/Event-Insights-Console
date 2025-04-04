# Flask libraries
from flask import Blueprint

# Controllers
from controllers.event_mapping_controller import EventMappingController

bp = Blueprint('event_mappings', __name__, url_prefix='/api/event-mapping')

@bp.route('', methods=['GET'])
def get_event_mappings():
    return EventMappingController.get_event_mapping()

@bp.route('', methods=['POST'])
def post_event_mappings():
    return EventMappingController.post_event_mapping()

@bp.route('<int:mapping_id>', methods=['PUT'])
def update_event_mappings(mapping_id):
    return EventMappingController.update_event_mapping(mapping_id)