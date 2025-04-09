from flask import Blueprint, render_template

from services.event_mapping_columns_service import EventMappingColumnsService
from services.event_mapping_service import EventMappingService
from services.event_type_service import EventTypeService
from services.source_service import SourceService

bp = Blueprint('web', __name__)

@bp.route('/')
def menu():
    return render_template('index.html')

@bp.route('/event-types')
def show_event_types():
    event_types = EventTypeService.get_all_event_types()        
    return render_template('event_types.html', event_types=event_types)

@bp.route('/event-mappings')
def show_event_mappings():
    mappings = EventMappingService.get_all_event_mappings()
    sources = SourceService.get_all_sources()
    event_types = EventTypeService.get_all_event_types()        
    return render_template('event_mappings.html', mappings=mappings, sources=sources, event_types=event_types)

@bp.route('/event-mappings/<int:mapping_id>')
def show_event_mapping_by_id(mapping_id):
    mapping = EventMappingService.get_event_mapping_by_pk(mapping_id)
    if not mapping:
        return "NOT FOUND", 404

    source_id = mapping.get("source_id")
    if not source_id:
        return "Not source id", 500
    source_data = SourceService.get_source_by_pk(source_id)
    actual_source = source_data.get("source_name")

    event_type_id = mapping.get("event_type_id")
    if not event_type_id:
        return "Not event type id", 500
    event_type_data = EventTypeService.get_event_type_by_pk(event_type_id)
    actual_event_type = event_type_data.get("event_type_name")
    
    columns = EventMappingColumnsService.get_all_mapping_columns(mapping_id)
    sources = SourceService.get_all_sources()
    event_types = EventTypeService.get_all_event_types()

    return render_template('mapping.html', mapping=mapping, columns=columns, actual_source=actual_source, actual_event_type=actual_event_type, sources=sources, event_types=event_types)
