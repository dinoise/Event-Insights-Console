from flask import Blueprint, render_template

from services.event_mapping_service import EventMappingService

bp = Blueprint('web', __name__)

@bp.route('/event-mappings')
def show_event_mappings():
    mappings = EventMappingService.get_all_event_mappings()        
    return render_template('index.html', mappings=mappings)

@bp.route('/event-mappings/<int:mapping_id>')
def show_event_mapping_by_id(mapping_id):
    try:
        mapping = EventMappingService.get_all_event_mapping_by_id(mapping_id)
    except Exception as e:
        print(e)
    print(mapping)     

    return render_template('mapping.html', mapping=mapping)