# ===================================
# Module and Service Imports
# ===================================
from flask import Blueprint, render_template, current_app
from services.event_mapping_columns_service import EventMappingColumnsService
from services.ingestion_events_service import IngestionEventService
from services.event_mapping_service import EventMappingService
from services.event_type_service import EventTypeService
from services.source_service import SourceService

# ===================================
# Utils
# ===================================
from utils.utils import get_secret

# ==============================
# Blueprint Configuration
# ==============================
bp = Blueprint('web', __name__)

# ==============================
# Application Routes
# ==============================

# Main route: Home menu
@bp.route('/')
def menu():
    return render_template('index.html')

# ==================================
# Event Mappings Routes
# ==================================

# Display all event mappings
@bp.route('/event-mappings')
def show_event_mappings():
    mappings = EventMappingService.get_all_event_mappings()
    sources = SourceService.get_all_sources()
    event_types = EventTypeService.get_all_event_types()        
    return render_template('event_mappings.html', mappings=mappings, sources=sources, event_types=event_types)

# Display event mapping details by ID
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

    return render_template('event_mapping_detail.html', mapping=mapping, columns=columns, actual_source=actual_source, actual_event_type=actual_event_type, sources=sources, event_types=event_types)

# ==================================
# Event Types Routes
# ==================================

# Display all event types
@bp.route('/event-types')
def show_event_types():
    event_types = EventTypeService.get_all_event_types()        
    return render_template('event_types.html', event_types=event_types)

# Display event type details by ID
@bp.route('/event-types/<int:event_type_id>')
def show_event_type_by_id(event_type_id):
    event_type = EventTypeService.get_event_type_by_pk(event_type_id)    
    associated_mappings = EventMappingService.get_all_event_mappings_by_event_type_id(event_type_id)
    return render_template('event_type_detail.html', event_type=event_type, associated_mappings=associated_mappings)

# ==================================
# Sources Routes
# ==================================

# Display all sources
@bp.route('/sources')
def show_sources():
    sources = SourceService.get_all_sources()   
    return render_template('sources.html', sources=sources)

# Display source details by ID
@bp.route('/sources/<int:source_id>')
def show_source_type_by_id(source_id):
    source = SourceService.get_source_by_pk(source_id)
    associated_mappings = EventMappingService.get_all_event_mappings_by_source_id(source_id)
    return render_template('source_detail.html', source=source, associated_mappings=associated_mappings)

# ==================================
# History of Events Routes
# ==================================

@bp.route('/history')
def show_history():
    return render_template('history.html')

@bp.route('/history/<string:ingestion_event_id>')
def show_history_by_uuid(ingestion_event_id):
    project_id = current_app.config.get('PROJECT_ID')
    dataset = get_secret( current_app.config.get('BIGQUERY_DATASET_DELIVERNOW_EVENTS') )
    tbl_ingestion_events = get_secret( current_app.config.get('BIGQUERY_TBL_INGESTION_EVENT') )

    ingestion_event = IngestionEventService.get_event_by_uuid(project_id=project_id, 
                                                    dataset=dataset,
                                                    tbl_ingestion_events=tbl_ingestion_events,
                                                    ingestion_event_id=ingestion_event_id)

    return render_template('history_detail.html', ingestion_event=ingestion_event)
