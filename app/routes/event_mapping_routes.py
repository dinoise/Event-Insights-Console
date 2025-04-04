# Flask libraries
from flask import Blueprint

# Controllers
from controllers.event_mapping_controller import EventMappingController

bp = Blueprint('event_mappings', __name__, url_prefix='/api/event-mappings')

@bp.route('', methods=['GET'])
def get_event_mappings():
    return EventMappingController.get_event_mappings()

@bp.route('', methods=['POST'])
def post_event_mappings():
    return EventMappingController.post_event_mappings()