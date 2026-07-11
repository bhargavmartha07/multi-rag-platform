import os
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
}

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class StorageService:

    def __init__(self) -> None:

        self.upload_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "uploads",
            )
        )

        os.makedirs(
            self.upload_dir,
            exist_ok=True,
        )

    def validate_file(
        self,
        file: UploadFile,
    ) -> None:

        if file.content_type not in ALLOWED_MIME_TYPES:

            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    f"File type '{file.content_type}' is not supported. "
                    f"Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
                ),
            )

    async def save_file(
        self,
        file: UploadFile,
        tenant_id: str,
    ) -> tuple[str, str, int]:

        file_ext = os.path.splitext(
            file.filename or "unknown"
        )[1]

        stored_filename = (
            f"{tenant_id}_{uuid.uuid4().hex}{file_ext}"
        )

        tenant_dir = os.path.join(
            self.upload_dir,
            tenant_id,
        )

        os.makedirs(
            tenant_dir,
            exist_ok=True,
        )

        file_path = os.path.join(
            tenant_dir,
            stored_filename
        )

        content = await file.read()

        if len(content) > MAX_FILE_SIZE_BYTES:

            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"File size exceeds maximum of {MAX_FILE_SIZE_MB}MB"
                ),
            )

        with open(file_path, "wb") as f:

            f.write(content)

        return stored_filename, file_path, len(content)


storage_service = StorageService()
