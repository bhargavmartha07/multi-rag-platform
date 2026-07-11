class TestHealthEndpoint:

    def test_health_returns_ok(self, client):

        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "healthy"


class TestRootEndpoint:

    def test_root_returns_message(self, client):

        response = client.get("/")

        assert response.status_code == 200

        data = response.json()

        assert "Enterprise RAG Platform" in data["message"]


class TestUserRegistration:

    def test_register_success(self, client):

        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert "id" in data

        assert data["email"] == "new@example.com"

        assert "tenant_id" in data

        assert len(data["tenant_id"]) > 0

    def test_register_duplicate_email(
        self, client, test_user
    ):

        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 409

    def test_register_duplicate_username(
        self, client, test_user
    ):

        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 409

    def test_register_weak_password(self, client):

        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "123",
            },
        )

        assert response.status_code == 422

    def test_register_invalid_email(self, client):

        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "bademail",
                "email": "not-an-email",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 422


class TestUserLogin:

    def test_login_success(self, client, test_user):

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert "access_token" in data

        assert data["token_type"] == "bearer"

    def test_login_wrong_password(
        self, client, test_user
    ):

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword!",
            },
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nobody@example.com",
                "password": "whatever",
            },
        )

        assert response.status_code == 401


class TestProtectedEndpoint:

    def test_me_without_token(self, client):

        response = client.get("/api/v1/auth/me")

        assert response.status_code in [401, 403]

    def test_me_with_valid_token(
        self, client, auth_headers
    ):

        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["email"] == "test@example.com"

        assert "tenant_id" in data

    def test_me_with_invalid_token(self, client):

        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid_token"
            },
        )

        assert response.status_code == 401
