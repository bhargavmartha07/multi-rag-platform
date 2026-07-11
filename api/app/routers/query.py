from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.query import (
    QueryRequest,
    QueryResponse,
)
from app.services.query_service import (
    query_service,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Query"],
)


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query_rag(
    request: QueryRequest,
    response: Response,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> QueryResponse:

    query_response, cache_hit = (
        query_service.query(
            query_text=request.query,
            tenant_id=current_user.tenant_id,
        )
    )

    response.headers["X-Cache-Hit"] = (
        "true" if cache_hit else "false"
    )

    return query_response
