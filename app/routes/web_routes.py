from flask import Blueprint, render_template

from services.event_mapping_service import EventMappingService
from services.event_mapping_columns_service import EventMappingColumnsService

bp = Blueprint('web', __name__)

@bp.route('/event-mappings')
def show_event_mappings():
    mappings = EventMappingService.get_all_event_mappings()        
    return render_template('index.html', mappings=mappings)

@bp.route('/event-mappings/<int:mapping_id>')
def show_event_mapping_by_id(mapping_id):
    mapping = EventMappingService.get_all_event_mapping_by_id(mapping_id)

    columns = EventMappingColumnsService.get_all_mapping_columns(mapping_id)

    return render_template('mapping.html', mapping=mapping, columns=columns)
