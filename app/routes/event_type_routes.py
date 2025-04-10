from flask import Blueprint
from controllers.event_type_controller import EventTypeController

bp = Blueprint('event_types', __name__, url_prefix='/api/event-types')

@bp.route('', methods=['GET'])
def get_event_types():
    return EventTypeController.get_event_types()

@bp.route('', methods=['POST'])
def post_event_types():
    return EventTypeController.post_event_mapping()

@bp.route('<int:event_type>', methods=['PUT'])
def update_event_type(event_type):
    return EventTypeController.update_event_type(event_type)

@bp.route('<int:event_type>', methods=['DELETE'])
def delete_event_type(event_type):
    return EventTypeController.delete_event_type(event_type)
