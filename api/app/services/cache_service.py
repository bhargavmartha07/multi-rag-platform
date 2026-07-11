import hashlib
import json
import logging
import os

import redis

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 3600


class CacheService:

    def __init__(self) -> None:

        redis_url = os.environ.get(
            "REDIS_URL",
            "redis://redis:6379/0",
        )

        self.client = redis.from_url(
            redis_url,
            decode_responses=True,
        )

    def _build_key(
        self,
        tenant_id: str,
        query_text: str,
    ) -> str:

        query_hash = hashlib.sha256(
            query_text.encode()
        ).hexdigest()[:16]

        return f"rag:query:{tenant_id}:{query_hash}"

    def get_cached_response(
        self,
        tenant_id: str,
        query_text: str,
    ) -> dict | None:

        key = self._build_key(
            tenant_id,
            query_text,
        )

        try:

            cached = self.client.get(key)

            if cached is not None:

                logger.info(
                    "Cache hit for tenant=%s query_hash=%s",
                    tenant_id,
                    key.split(":")[-1],
                )

                return json.loads(cached)

            return None

        except Exception as e:

            logger.warning(
                "Cache get failed: %s",
                str(e),
            )

            return None

    def set_cached_response(
        self,
        tenant_id: str,
        query_text: str,
        response_data: dict,
        ttl: int = CACHE_TTL_SECONDS,
    ) -> None:

        key = self._build_key(
            tenant_id,
            query_text,
        )

        try:

            self.client.setex(
                key,
                ttl,
                json.dumps(response_data),
            )

            logger.info(
                "Cache set for tenant=%s ttl=%d",
                tenant_id,
                ttl,
            )

        except Exception as e:

            logger.warning(
                "Cache set failed: %s",
                str(e),
            )


cache_service = CacheService()
