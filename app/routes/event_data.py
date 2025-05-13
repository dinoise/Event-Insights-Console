from flask import Blueprint
from controllers.event_data_controller import EventDataController

bp = Blueprint('event_data', __name__, url_prefix='/api/event-data')

@bp.route('/', methods=['GET'])
def embedding_search():
    return EventDataController.get_event_client_data()