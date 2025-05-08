from flask import Blueprint
from controllers.event_embeddings_controller import EventEmbeddingController

bp = Blueprint('event_embeddings', __name__, url_prefix='/api/embeddings')

@bp.route('/', methods=['GET'])
def embedding_search():
    return EventEmbeddingController.embedding_search()