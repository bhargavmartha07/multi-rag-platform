import logging

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.celery_client import celery_client
from app.dependencies.storage import storage_service
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.repositories.document_repository import (
    document_repository,
)
from app.schemas.document import (
    DocumentStatusResponse,
    DocumentUploadResponse,
)

logger = logging.getLogger(__name__)


class DocumentService:

    @staticmethod
    async def upload_document(
        db: Session,
        file: UploadFile,
        user_id: int,
        tenant_id: str,
    ) -> DocumentUploadResponse:

        storage_service.validate_file(file)

        stored_filename, file_path, file_size = (
            await storage_service.save_file(
                file,
                tenant_id,
            )
        )

        document = Document(
            tenant_id=tenant_id,
            owner_id=user_id,
            filename=file.filename or "unknown",
            stored_filename=stored_filename,
            mime_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            status=DocumentStatus.UPLOADED.value,
        )

        created_doc = document_repository.create(
            db,
            document,
        )

        logger.info(
            "Document uploaded: id=%d tenant=%s filename=%s",
            created_doc.id,
            tenant_id,
            created_doc.filename,
        )

        try:

            celery_client.send_task(
                "app.tasks.process_document",
                kwargs={
                    "document_id": created_doc.id,
                    "tenant_id": tenant_id,
                    "file_path": file_path,
                },
            )

            document_repository.update_status(
                db,
                created_doc.id,
                tenant_id,
                DocumentStatus.PROCESSING,
            )

            logger.info(
                "Dispatched processing task for document %d",
                created_doc.id,
            )

        except Exception as e:

            logger.error(
                "Failed to dispatch processing task for document %d: %s",
                created_doc.id,
                str(e),
            )

            document_repository.update_status(
                db,
                created_doc.id,
                tenant_id,
                DocumentStatus.FAILED,
                error_message=str(e),
            )

        return DocumentUploadResponse(
            document_id=created_doc.id,
            filename=created_doc.filename,
            status=DocumentStatus.PROCESSING.value,
        )

    @staticmethod
    def get_document_status(
        db: Session,
        document_id: int,
        tenant_id: str,
    ) -> DocumentStatusResponse:

        document = document_repository.get_by_id(
            db,
            document_id,
            tenant_id,
        )

        if document is None:

            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        return DocumentStatusResponse(
            document_id=document.id,
            status=document.status,
            filename=document.filename,
            chunk_count=document.chunk_count,
            error_message=document.error_message,
            created_at=document.created_at,
        )


document_service = DocumentService()
