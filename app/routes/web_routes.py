from flask import Blueprint, render_template

from services.event_mapping_service import EventMappingService

bp = Blueprint('web', __name__)

@bp.route('/event-mappings')
def show_event_mappings():
    mappings = EventMappingService.get_all_event_mappings()        
    return render_template('index.html', mappings=mappings)
