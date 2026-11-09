def test_register_client_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "developer_1", "tier": "basic", "secret": "supersecure123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "developer_1"
    assert data["tier"] == "basic"
    assert "id" in data
    assert "jwt_secret" not in data


def test_register_client_duplicate_conflict(client):
    payload = {"name": "unique_dev", "tier": "premium", "secret": "secretpassword"}
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409


def test_issue_token_success(client, create_test_client):
    create_test_client(name="token_user", tier="premium", secret="mypassword")

    response = client.post(
        "/api/v1/auth/tokens",
        data={"username": "token_user", "password": "mypassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_issue_token_invalid_password(client, create_test_client):
    create_test_client(name="token_user2", tier="basic", secret="correctpass")

    response = client.post(
        "/api/v1/auth/tokens",
        data={"username": "token_user2", "password": "wrongpassword"},
    )
    assert response.status_code == 401

