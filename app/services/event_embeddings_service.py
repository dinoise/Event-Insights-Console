from models.event_embeddings import EventEmbedding
from schemas.event_embeddings_schema import EventEmbeddingSchema

class EventEmbeddingService:

    @staticmethod
    def embedding_search(
        query_embedding: list[float], 
        similarity_threshold: float, 
        top_k: int
    ) -> dict[str, any]:
        distance = EventEmbedding.embedding_embedded_message.cosine_distance(query_embedding)

        query = (
            EventEmbedding.query
            .filter(distance < similarity_threshold)
            .order_by(distance)
            .limit(top_k)
        )

        results = query.all()

        return EventEmbeddingSchema(many=True).dump(results)