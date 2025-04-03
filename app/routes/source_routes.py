from flask import Blueprint
from controllers.source_controller import SourceController

bp = Blueprint('sources', __name__, url_prefix='/api/sources')

@bp.route('', methods=['GET'])
def get_sources():
    return SourceController.get_sources()
