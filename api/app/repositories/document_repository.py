from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import DocumentStatus


class DocumentRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: int,
        tenant_id: str,
    ) -> Document | None:

        stmt = (
            select(Document)
            .where(
                Document.id == document_id,
                Document.tenant_id == tenant_id,
            )
        )

        return db.execute(
            stmt
        ).scalar_one_or_none()

    @staticmethod
    def get_by_id_any_tenant(
        db: Session,
        document_id: int,
    ) -> Document | None:

        stmt = (
            select(Document)
            .where(Document.id == document_id)
        )

        return db.execute(
            stmt
        ).scalar_one_or_none()

    @staticmethod
    def list_by_tenant(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Document]:

        stmt = (
            select(Document)
            .where(Document.tenant_id == tenant_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.execute(stmt).scalars().all()
        )

    @staticmethod
    def create(
        db: Session,
        document: Document,
    ) -> Document:

        try:

            db.add(document)
            db.commit()
            db.refresh(document)

            return document

        except IntegrityError:

            db.rollback()
            raise

    @staticmethod
    def update_status(
        db: Session,
        document_id: int,
        tenant_id: str,
        status: DocumentStatus,
        error_message: str | None = None,
        chunk_count: int | None = None,
    ) -> Document | None:

        document = DocumentRepository.get_by_id(
            db,
            document_id,
            tenant_id,
        )

        if document is None:

            return None

        document.status = status.value

        if error_message is not None:

            document.error_message = error_message

        if chunk_count is not None:

            document.chunk_count = chunk_count

        db.commit()
        db.refresh(document)

        return document


document_repository = DocumentRepository()
