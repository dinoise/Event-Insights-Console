from flask import Blueprint, jsonify, request, session, current_app
from http import HTTPStatus

bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@bp.route('/call', methods=['POST'])
def handle_response():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No data"}), HTTPStatus.BAD_REQUEST
    
    prompt = json_data.get("prompt", None)
    if not prompt:
        return jsonify({"error": "No user query"}), HTTPStatus.BAD_REQUEST
    
    if "uuid" not in session:
        return jsonify({"error": "Invoke index handler before start chatting"}), HTTPStatus.BAD_REQUEST
    
    orchestrator = current_app.orchestrator

    try:
        response = orchestrator.process_message(session["uuid"], prompt)
        return jsonify(response), HTTPStatus.OK
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({
            "type": "message", 
            "content": "Lo siento, ocurrió un error al procesar tu mensaje"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/reset', methods=['POST'])
def reset_conversation():
    if "uuid" not in session:
        return jsonify({"error": "No session to reset"}), HTTPStatus.BAD_REQUEST
    
    session_uuid = session["uuid"]
    orchestrator = current_app.orchestrator

    if not orchestrator.user_session_exists(session_uuid):
        return jsonify({"error": "Current user session not found"}), HTTPStatus.INTERNAL_SERVER_ERROR

    orchestrator.user_session_reset(session_uuid)
    return jsonify({"status": "conversation reset"}), HTTPStatus.OK