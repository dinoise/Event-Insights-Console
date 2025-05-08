from flask import Blueprint, jsonify, request, session, current_app
from http import HTTPStatus

bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@bp.route('/call', methods=['POST'])
def handle_response():
    json_data = request.get_json()
    if not json_data:
        return jsonify(
            {
                "error": "No data"
            }, 400
        )
    
    prompt = json_data.get("prompt", None)
    if not prompt:
        return jsonify(
            {
                "error": "No user query"
            }, 400
        )
    
    if "uuid" not in session:
        return jsonify(
            {
                "error": "Invoke index handler before start chatting"
            }, 400
        )
    
    orchestrator = current_app.orchestrator

    try:
        response = orchestrator.process_message(session["uuid"], prompt)
    except Exception as e:
        print(e)
        jsonify( {"type": "message", "content": "Lo siento, inténtalo más tarde"} ), HTTPStatus.INTERNAL_SERVER_ERROR
    
    return jsonify( response ), HTTPStatus.OK

