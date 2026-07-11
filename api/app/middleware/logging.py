import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

logger = logging.getLogger("rag_api.access")


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        request_id = str(uuid.uuid4())[:8]

        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            "request_id=%s method=%s path=%s status=%d duration=%.4fs",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        response.headers["X-Request-ID"] = (
            request_id
        )

        return response
