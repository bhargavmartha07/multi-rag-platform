import logging
import os

from openai import OpenAI

from app.schemas.query import (
    QueryResponse,
    SourceDocument,
)
from app.services.cache_service import (
    cache_service,
)
from app.services.embedding_service import (
    embedding_service,
)
from app.services.vector_service import (
    vector_service,
)

logger = logging.getLogger(__name__)

LLM_MODEL = "gpt-3.5-turbo"


class QueryService:

    def __init__(self) -> None:

        api_key = os.environ.get(
            "OPENAI_API_KEY", ""
        )

        self.llm_client = OpenAI(api_key=api_key)

    def query(
        self,
        query_text: str,
        tenant_id: str,
    ) -> tuple[QueryResponse, bool]:

        cached = cache_service.get_cached_response(
            tenant_id,
            query_text,
        )

        if cached is not None:

            return (
                QueryResponse(**cached),
                True,
            )

        query_embedding = (
            embedding_service.generate_single_embedding(
                query_text,
            )
        )

        search_results = vector_service.search(
            query_embedding=query_embedding,
            tenant_id=tenant_id,
            top_k=5,
        )

        if not search_results:

            response = QueryResponse(
                answer="I don't have enough information to answer this question based on the available documents.",
                sources=[],
            )

            cache_service.set_cached_response(
                tenant_id,
                query_text,
                response.model_dump(),
            )

            return response, False

        context_parts = []

        sources = []

        seen_doc_ids = set()

        for result in search_results:

            payload = result["payload"]

            text = payload.get("text", "")

            doc_id = payload.get("document_id", 0)

            context_parts.append(text)

            if doc_id not in seen_doc_ids:

                sources.append(
                    SourceDocument(
                        document_id=doc_id,
                        content=text[:500],
                    )
                )

                seen_doc_ids.add(doc_id)

        context = "\n\n---\n\n".join(
            context_parts
        )

        prompt = (
            "You are a helpful assistant. Answer the following question "
            "based on the provided context. If the context doesn't contain "
            "enough information, say so. Always cite which document you "
            "are referencing.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query_text}\n\n"
            "Answer:"
        )

        try:

            response = (
                self.llm_client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on provided documents.",
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                )
            )

            answer = response.choices[
                0
            ].message.content

            if answer is None:

                answer = "I was unable to generate a response."

            tokens_used = (
                response.usage.total_tokens
                if response.usage
                else 0
            )

            logger.info(
                "Query processed: tokens=%d results=%d",
                tokens_used,
                len(search_results),
            )

        except Exception as e:

            logger.error(
                "LLM query failed: %s",
                str(e),
            )

            answer = (
                "An error occurred while generating the response. "
                "Please try again later."
            )

        query_response = QueryResponse(
            answer=answer,
            sources=sources,
        )

        cache_service.set_cached_response(
            tenant_id,
            query_text,
            query_response.model_dump(),
        )

        return query_response, False


query_service = QueryService()
