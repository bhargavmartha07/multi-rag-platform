import logging
import os

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.celery_app import celery_app
from app.chunking import chunk_text

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/rag_platform",
)

QDRANT_URL = os.environ.get(
    "QDRANT_URL",
    "http://qdrant:6333",
)

EMBEDDING_PROVIDER = os.environ.get(
    "EMBEDDING_PROVIDER",
    "ollama",
)

OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434/v1",
)

EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL",
    "nomic-embed-text",
)

EMBEDDING_DIMENSIONS = int(
    os.environ.get(
        "EMBEDDING_DIMENSIONS",
        "768",
    )
)

COLLECTION_NAME = "rag_documents"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)


def _ensure_collection():
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
    )

    client = QdrantClient(url=QDRANT_URL)

    collections = client.get_collections()

    collection_names = [
        c.name for c in collections.collections
    ]

    if COLLECTION_NAME not in collection_names:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSIONS,
                distance=Distance.COSINE,
            ),
        )

        logger.info(
            "Created Qdrant collection: %s (size=%d)",
            COLLECTION_NAME,
            EMBEDDING_DIMENSIONS,
        )

    client.close()


def _extract_text(file_path: str) -> str:

    if file_path.endswith(".pdf"):

        from pypdf import PdfReader

        reader = PdfReader(file_path)

        text_parts = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text_parts.append(page_text)

        return "\n\n".join(text_parts)

    elif file_path.endswith(
        (".txt", ".md")
    ):

        with open(file_path, "r", encoding="utf-8") as f:

            return f.read()

    else:

        raise ValueError(
            f"Unsupported file type: {file_path}"
        )


def _generate_embeddings(
    texts: list[str],
) -> list[list[float]]:

    from openai import OpenAI

    if EMBEDDING_PROVIDER == "ollama":

        client = OpenAI(
            api_key="ollama",
            base_url=OLLAMA_BASE_URL,
        )

    else:

        api_key = os.environ.get("OPENAI_API_KEY", "")

        client = OpenAI(api_key=api_key)

    batch_size = 20

    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):

        batch = texts[i : i + batch_size]

        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )

        batch_embeddings = [
            item.embedding
            for item in response.data
        ]

        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def _store_in_qdrant(
    embeddings: list[list[float]],
    chunks: list[str],
    document_id: int,
    tenant_id: str,
) -> int:

    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        PointStruct,
    )

    client = QdrantClient(url=QDRANT_URL)

    points = []

    for i, (embedding, chunk) in enumerate(
        zip(embeddings, chunks)
    ):

        points.append(
            PointStruct(
                id=document_id * 100000 + i,
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "tenant_id": tenant_id,
                    "chunk_index": i,
                    "text": chunk,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    client.close()

    return len(points)


def _update_document_status(
    document_id: int,
    status: str,
    chunk_count: int = 0,
    error_message: str | None = None,
):

    from app.models_document import Document

    db = SessionLocal()

    try:

        stmt = select(Document).where(
            Document.id == document_id
        )

        document = db.execute(
            stmt
        ).scalar_one_or_none()

        if document is not None:

            document.status = status

            if chunk_count > 0:

                document.chunk_count = chunk_count

            if error_message is not None:

                document.error_message = error_message

            db.commit()

    except Exception as e:

        db.rollback()

        logger.error(
            "Failed to update document %d status: %s",
            document_id,
            str(e),
        )

        raise

    finally:

        db.close()


@celery_app.task(
    bind=True,
    name="app.tasks.process_document",
    max_retries=3,
    default_retry_delay=60,
)
def process_document_task(
    self,
    document_id: int,
    tenant_id: str,
    file_path: str,
):

    logger.info(
        "Starting document processing: id=%d tenant=%s",
        document_id,
        tenant_id,
    )

    try:

        _update_document_status(
            document_id,
            "processing",
        )

        text = _extract_text(file_path)

        if not text.strip():

            _update_document_status(
                document_id,
                "failed",
                error_message="No text content could be extracted from the document.",
            )

            return

        chunks = chunk_text(text)

        if not chunks:

            _update_document_status(
                document_id,
                "failed",
                error_message="Document produced no chunks after processing.",
            )

            return

        embeddings = _generate_embeddings(chunks)

        _ensure_collection()

        stored_count = _store_in_qdrant(
            embeddings,
            chunks,
            document_id,
            tenant_id,
        )

        _update_document_status(
            document_id,
            "completed",
            chunk_count=stored_count,
        )

        logger.info(
            "Document processing completed: id=%d chunks=%d",
            document_id,
            stored_count,
        )

    except Exception as exc:

        logger.error(
            "Document processing failed: id=%d error=%s",
            document_id,
            str(exc),
        )

        _update_document_status(
            document_id,
            "failed",
            error_message=str(exc),
        )

        raise self.retry(exc=exc)
