from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):

    document_id: int
    filename: str
    status: str


class DocumentStatusResponse(BaseModel):

    document_id: int
    status: str
    filename: str
    chunk_count: int
    error_message: str | None
    created_at: datetime
