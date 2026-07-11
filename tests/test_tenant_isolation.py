import io


class TestTenantIsolation:

    def test_user_a_cannot_see_user_b_documents(
        self,
        client,
        auth_headers,
        auth_headers_b,
    ):

        upload_a = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "secret_a.pdf",
                    io.BytesIO(b"Secret A content"),
                    "application/pdf",
                )
            },
        )

        doc_a_id = upload_a.json()["document_id"]

        status_b = client.get(
            f"/api/v1/documents/{doc_a_id}/status",
            headers=auth_headers_b,
        )

        assert status_b.status_code == 404

    def test_user_b_query_does_not_return_user_a_sources(
        self,
        client,
        auth_headers,
        auth_headers_b,
    ):

        client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "exclusive.pdf",
                    io.BytesIO(
                        b"The Zargothian fleet flies at dawn."
                    ),
                    "application/pdf",
                )
            },
        )

        client.post(
            "/api/v1/documents",
            headers=auth_headers_b,
            files={
                "file": (
                    "other.pdf",
                    io.BytesIO(
                        b"Something completely different."
                    ),
                    "application/pdf",
                )
            },
        )

        response_b = client.post(
            "/api/v1/query",
            headers=auth_headers_b,
            json={
                "query": "What does the Zargothian fleet do?"
            },
        )

        assert response_b.status_code == 200

        data_b = response_b.json()

        source_doc_ids = [
            s["document_id"] for s in data_b["sources"]
        ]

        assert doc_a_id not in source_doc_ids

    def test_user_a_query_returns_own_sources(
        self,
        client,
        auth_headers,
    ):

        upload_response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={
                "file": (
                    "own_doc.pdf",
                    io.BytesIO(
                        b"The Zargothian fleet flies at dawn."
                    ),
                    "application/pdf",
                )
            },
        )

        doc_id = upload_response.json()["document_id"]

        response_a = client.post(
            "/api/v1/query",
            headers=auth_headers,
            json={
                "query": "What does the Zargothian fleet do?"
            },
        )

        assert response_a.status_code == 200

        data_a = response_a.json()

        source_doc_ids = [
            s["document_id"] for s in data_a["sources"]
        ]

        assert doc_id in source_doc_ids
