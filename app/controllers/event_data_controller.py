from flask import jsonify, request, current_app
from http import HTTPStatus

from services.event_data_service import EventDataService
from utils.utils import get_secret

class EventDataController:

    @staticmethod
    def get_event_client_data():
        id_cliente = request.args.get('id_cliente', default=None, type=str)
        if not id_cliente:
            return jsonify({
                "message": "id_cliente is missing",
                "data":  None
            }), HTTPStatus.BAD_REQUEST

        project_id = current_app.config.get("PROJECT_ID")
        dataset = get_secret( current_app.config.get("BIGQUERY_DATASET") )
        table = get_secret( current_app.config.get("BIGQUERY_TBL_CLIENTES") )

        try:
            result = EventDataService.get_table_columns(project_id=project_id,
                                            dataset=dataset,
                                            table=table,
                                            id_cliente=id_cliente)
        except Exception as e:
            print(e)
            return str(e), 500
        
        response = {
            "message": "success" if result else "Search was not succesful",
            "data": result if result else None
        }

        status = HTTPStatus.OK if result else HTTPStatus.NOT_FOUND
        return jsonify(response), status