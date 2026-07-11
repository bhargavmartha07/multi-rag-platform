import io


class TestDocumentUpload:

    def test_upload_requires_auth(self, client):

        response = client.post(
            "/api/v1/documents",
            files={
                "file": (
                    "test.pdf",
                    b"fake pdf content",
                    "application/pdf",
                )
            },
        )

        assert response.status_code in [401, 403]

    def test_upload_pdf_success(
        self, client, auth_headers
    ):

        pdf_content = b"%PDF-1.4 fake content"

        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "test.pdf",
                    io.BytesIO(pdf_content),
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 202

        data = response.json()

        assert "document_id" in data

        assert data["filename"] == "test.pdf"

        assert data["status"] == "processing"

    def test_upload_txt_success(
        self, client, auth_headers
    ):

        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "notes.txt",
                    b"This is a test document.",
                    "text/plain",
                )
            },
        )

        assert response.status_code == 202

    def test_upload_invalid_file_type(
        self, client, auth_headers
    ):

        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "script.exe",
                    b"binary content",
                    "application/octet-stream",
                )
            },
        )

        assert response.status_code == 415


class TestDocumentStatus:

    def test_status_requires_auth(self, client):

        response = client.get(
            "/api/v1/documents/1/status"
        )

        assert response.status_code in [401, 403]

    def test_status_nonexistent_document(
        self, client, auth_headers
    ):

        response = client.get(
            "/api/v1/documents/99999/status",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_status_returns_correct_schema(
        self, client, auth_headers
    ):

        pdf_content = b"%PDF-1.4 test doc"

        upload_response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "status_test.pdf",
                    io.BytesIO(pdf_content),
                    "application/pdf",
                )
            },
        )

        doc_id = upload_response.json()["document_id"]

        status_response = client.get(
            f"/api/v1/documents/{doc_id}/status",
            headers=auth_headers,
        )

        assert status_response.status_code == 200

        data = status_response.json()

        assert data["document_id"] == doc_id

        assert data["status"] in [
            "uploaded",
            "processing",
            "completed",
            "failed",
        ]

        assert data["filename"] == "status_test.pdf"

        assert "chunk_count" in data

        assert "created_at" in data
