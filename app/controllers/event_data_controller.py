from flask import jsonify, request, current_app
from http import HTTPStatus

from services.event_data_service import EventDataService

class EventDataController:

    @staticmethod
    def get_generic_event_data():
        event_uuid = request.args.get('event_uuid', default=None, type=str)
        target_dataset = request.args.get('target_dataset', default=None, type=str)
        target_table = request.args.get('target_table', default=None, type=str)

        if not event_uuid or not target_dataset or not target_table:
            return jsonify({
                "message": "event_uuid, target_dataset and target_table are mandatory",
                "data": []
            }), HTTPStatus.BAD_REQUEST

        project_id = current_app.config.get("PROJECT_ID")

        try:
            result = EventDataService.get_table_columns(project_id=project_id,
                                            dataset=target_dataset,
                                            table=target_table,
                                            event_uuid=event_uuid)
        except Exception as e:
            print(e)
            return str(e), 500
        
        response = {
            "message": "success" if result else "Search was not succesful",
            "data": result if result else None
        }

        status = HTTPStatus.OK if result else HTTPStatus.NOT_FOUND
        return jsonify(response), status