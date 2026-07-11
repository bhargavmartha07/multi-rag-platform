import io


class TestQueryEndpoint:

    def test_query_requires_auth(self, client):

        response = client.post(
            "/api/v1/query",
            json={"query": "What is this about?"},
        )

        assert response.status_code in [401, 403]

    def test_query_returns_response(
        self, client, auth_headers
    ):

        response = client.post(
            "/api/v1/query",
            headers=auth_headers,
            json={"query": "What documents do I have?"},
        )

        assert response.status_code == 200

        data = response.json()

        assert "answer" in data

        assert "sources" in data

        assert isinstance(data["sources"], list)

    def test_query_includes_cache_header(
        self, client, auth_headers
    ):

        response = client.post(
            "/api/v1/query",
            headers=auth_headers,
            json={
                "query": "Test cache header"
            },
        )

        assert response.status_code == 200

        assert "x-cache-hit" in response.headers

        assert response.headers["x-cache-hit"] in [
            "true",
            "false",
        ]

    def test_query_with_empty_query(
        self, client, auth_headers
    ):

        response = client.post(
            "/api/v1/query",
            headers=auth_headers,
            json={"query": ""},
        )

        assert response.status_code == 200
