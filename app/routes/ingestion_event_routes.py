from flask import Blueprint
from controllers.ingestion_events_contoller import IngestionEventController

bp = Blueprint('ingestion_events', __name__, url_prefix='/api/ingestion-events')

@bp.route('/', methods=['GET'])
def get_ingestion_events():
    return IngestionEventController.get_ingestion_events()