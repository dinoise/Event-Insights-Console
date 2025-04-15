# Flask libraries
from flask import jsonify, request, current_app

# Services
from services.ingestion_events_service import IngestionEventService

from http import HTTPStatus

from utils.utils import get_secret

class IngestionEventController:

    @staticmethod
    def get_ingestion_events() -> tuple:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=50, type=int)
        search = request.args.get('search', default="", type=str)
        
        if page < 1 or per_page < 1 or per_page > 1000:
            return jsonify({
                "status": HTTPStatus.BAD_REQUEST,
                "code": "invalid_parameters",
                "message": "Invalid pagination parameters. Page must be >= 1 and per_page between 1-1000"
            }), HTTPStatus.BAD_REQUEST
        
        project_id = current_app.config.get('PROJECT_ID')
        dataset = get_secret( current_app.config.get('BIGQUERY_DATASET') )
        tbl_clientes = get_secret( current_app.config.get('BIGQUERY_TBL_CLIENTES') )
        tbl_envios = get_secret( current_app.config.get('BIGQUERY_TBL_ENVIOS') )
        tbl_pedidos = get_secret( current_app.config.get('BIGQUERY_TBL_PEDIDOS') )

        ingestion_events = IngestionEventService.get_all_ingestion_events(
            project_id=project_id,
            dataset=dataset,
            tbl_clientes=tbl_clientes,
            tbl_envios=tbl_envios,
            tbl_pedidos=tbl_pedidos,
            page=page,
            per_page=per_page,
            search=search
        )
        
        total_events = IngestionEventService.get_total_count(
            project_id=project_id,
            dataset=dataset,
            tbl_clientes=tbl_clientes,
            tbl_envios=tbl_envios,
            tbl_pedidos=tbl_pedidos
        )
        
        total_pages = (total_events + per_page - 1) // per_page
        
        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": ingestion_events,
            "pagination": {
                "total": total_events,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }), HTTPStatus.OK
    
    @staticmethod
    def get_ingestion_event_by_uuid(ingestion_event_id: str) -> tuple:
        project_id = current_app.config.get('PROJECT_ID')
        dataset = get_secret( current_app.config.get('BIGQUERY_DATASET_DELIVERNOW_EVENTS') )
        tbl_ingestion_events = get_secret( current_app.config.get('BIGQUERY_TBL_INGESTION_EVENT') )
        
        try:
            ingestion_event = IngestionEventService.get_event_by_uuid(project_id=project_id, 
                                                    dataset=dataset,
                                                    tbl_ingestion_events=tbl_ingestion_events,
                                                    ingestion_event_id=ingestion_event_id)
        except Exception as e:
            error_msg = f"Error getting the ingestion event: {str(e)}"
            return jsonify({
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "code": "error",
                "message": error_msg
            }), HTTPStatus.INTERNAL_SERVER_ERROR

        if not ingestion_event:
            return jsonify({
                "status": HTTPStatus.NOT_FOUND,
                "code": "error",
                "data": None,
                "message": "No data for that UUID"
            }), HTTPStatus.NOT_FOUND
        
        return jsonify({
            "status": HTTPStatus.OK,
            "code": "success",
            "data": ingestion_event
        }), HTTPStatus.OK