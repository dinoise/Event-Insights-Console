from flask import Blueprint
from controllers.ingestion_events_contoller import IngestionEventController

bp = Blueprint('ingestion_events', __name__, url_prefix='/api/ingestion-events')

@bp.route('/', methods=['GET'])
def get_ingestion_events():
    return IngestionEventController.get_ingestion_events()

@bp.route('/<string:ingestion_event_id>', methods=['GET'])
def get_ingestion_event_by_id(ingestion_event_id):
    return IngestionEventController.get_ingestion_event_by_uuid(ingestion_event_id)