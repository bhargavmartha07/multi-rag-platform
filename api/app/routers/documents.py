from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    status,
)
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentStatusResponse,
    DocumentUploadResponse,
)
from app.services.document_service import (
    document_service,
)

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:

    return await document_service.upload_document(
        db,
        file,
        current_user.id,
        current_user.tenant_id,
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
)
def get_document_status(
    document_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> DocumentStatusResponse:

    return document_service.get_document_status(
        db,
        document_id,
        current_user.tenant_id,
    )
