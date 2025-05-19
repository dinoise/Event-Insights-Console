from flask import jsonify, request, current_app
from http import HTTPStatus

from services.event_embeddings_service import EventEmbeddingService

class EventEmbeddingController:

    @staticmethod
    def embedding_search():
        query = request.args.get('query', default=None, type=str)
        top_k = request.args.get('top_k', default=5, type=int)

        query_embedding = current_app.embed_service.embed_query(query)

        results = EventEmbeddingService.embedding_search(query_embedding=query_embedding,
                                                        similarity_threshold=0.5,
                                                        top_k=top_k)
        
        response = {
            "message": "success" if results else "Search was not succesful",
            "data": results if results else None
        }

        status = HTTPStatus.OK if results else HTTPStatus.NOT_FOUND
        return jsonify(response), status