import time
import logging

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
)
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_requests_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[
        0.01, 0.025, 0.05, 0.1, 0.25,
        0.5, 1.0, 2.5, 5.0, 10.0,
    ],
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Number of active HTTP requests",
)

RAG_QUERY_COUNT = Counter(
    "rag_query_total",
    "Total RAG queries processed",
    ["tenant_id"],
)

RAG_TOKENS_USED = Counter(
    "rag_query_tokens_used_total",
    "Total LLM tokens used in RAG queries",
)

DOCUMENT_UPLOAD_COUNT = Counter(
    "document_uploads_total",
    "Total document uploads",
    ["tenant_id"],
)


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        if request.url.path == "/metrics":

            return await call_next(request)

        method = request.method

        path = request.url.path

        ACTIVE_REQUESTS.inc()

        start_time = time.time()

        try:

            response = await call_next(request)

            duration = time.time() - start_time

            status_code = response.status_code

            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=str(status_code),
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path,
            ).observe(duration)

            return response

        except Exception as exc:

            duration = time.time() - start_time

            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code="500",
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path,
            ).observe(duration)

            raise

        finally:

            ACTIVE_REQUESTS.dec()
