from flask import Blueprint
from controllers.event_mapping_controller import EventMappingController

bp = Blueprint('event_mappings', __name__, url_prefix='/api/event-mappings')

@bp.route('', methods=['GET'])
def get_event_mappings():
    return EventMappingController.get_event_mappings()
