import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


class EmbeddingService:

    def __init__(self) -> None:

        api_key = os.environ.get(
            "OPENAI_API_KEY", ""
        )

        self.client = OpenAI(api_key=api_key)

    def generate_embeddings(
        self,
        texts: list[str],
        batch_size: int = 20,
    ) -> list[list[float]]:

        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):

            batch = texts[i : i + batch_size]

            try:

                response = (
                    self.client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=batch,
                    )
                )

                batch_embeddings = [
                    item.embedding
                    for item in response.data
                ]

                all_embeddings.extend(batch_embeddings)

                logger.info(
                    "Generated embeddings for batch %d-%d",
                    i,
                    i + len(batch),
                )

            except Exception as e:

                logger.error(
                    "Embedding generation failed for batch %d: %s",
                    i,
                    str(e),
                )

                raise

        return all_embeddings

    def generate_single_embedding(
        self,
        text: str,
    ) -> list[float]:

        return self.generate_embeddings([text])[0]


embedding_service = EmbeddingService()
