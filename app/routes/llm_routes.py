from flask import Blueprint, jsonify

bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@bp.route('', methods=['GET'])
def get_sources():
    return jsonify({
        "data": "data"
    }), 200
