import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(self) -> None:

        if settings.EMBEDDING_PROVIDER == "ollama":

            self.client = OpenAI(
                api_key="ollama",
                base_url=settings.OLLAMA_BASE_URL,
            )

            self.model = settings.EMBEDDING_MODEL

            self.dimensions = (
                settings.EMBEDDING_DIMENSIONS
            )

        else:

            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
            )

            self.model = (
                settings.OPENAI_EMBEDDING_MODEL
            )

            self.dimensions = (
                settings.OPENAI_EMBEDDING_DIMENSIONS
            )

        logger.info(
            "Embedding provider=%s model=%s dims=%d",
            settings.EMBEDDING_PROVIDER,
            self.model,
            self.dimensions,
        )

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
                        model=self.model,
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
