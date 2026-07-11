import logging
import os

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "rag_documents"


class VectorService:

    def __init__(self) -> None:

        self.qdrant_url = settings.QDRANT_URL

        self.vector_size = (
            settings.EMBEDDING_DIMENSIONS
            if settings.EMBEDDING_PROVIDER == "ollama"
            else settings.OPENAI_EMBEDDING_DIMENSIONS
        )

        self.client = QdrantClient(
            url=self.qdrant_url
        )

        logger.info(
            "VectorService: url=%s vector_size=%d",
            self.qdrant_url,
            self.vector_size,
        )

    def ensure_collection(self) -> None:

        collections = self.client.get_collections()

        collection_names = [
            c.name for c in collections.collections
        ]

        if COLLECTION_NAME not in collection_names:

            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(
                "Created Qdrant collection: %s (size=%d)",
                COLLECTION_NAME,
                self.vector_size,
            )

    def upsert_vectors(
        self,
        embeddings: list[list[float]],
        texts: list[str],
        document_id: int,
        tenant_id: str,
    ) -> int:

        self.ensure_collection()

        points = []

        for i, (embedding, text) in enumerate(
            zip(embeddings, texts)
        ):

            points.append(
                PointStruct(
                    id=document_id * 100000 + i,
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "tenant_id": tenant_id,
                        "chunk_index": i,
                        "text": text,
                    },
                )
            )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        logger.info(
            "Upserted %d vectors for document %d",
            len(points),
            document_id,
        )

        return len(points)

    def search(
        self,
        query_embedding: list[float],
        tenant_id: str,
        top_k: int = 5,
    ) -> list[dict]:

        self.ensure_collection()

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="tenant_id",
                        match=MatchValue(
                            value=tenant_id,
                        ),
                    )
                ]
            ),
            limit=top_k,
        )

        formatted_results = []

        for result in results:

            formatted_results.append(
                {
                    "score": result.score,
                    "payload": result.payload,
                }
            )

        logger.info(
            "Search returned %d results for tenant %s",
            len(formatted_results),
            tenant_id,
        )

        return formatted_results

    def delete_document_vectors(
        self,
        document_id: int,
        tenant_id: str,
    ) -> None:

        from qdrant_client.models import (
            PointIdsList,
        )

        point_ids = [
            document_id * 100000 + i
            for i in range(100000)
        ]

        try:

            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=PointIdsList(
                    points=point_ids,
                ),
            )

        except Exception as e:

            logger.warning(
                "Failed to delete vectors for document %d: %s",
                document_id,
                str(e),
            )


vector_service = VectorService()
