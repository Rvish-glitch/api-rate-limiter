def test_get_me_authenticated(client, auth_headers):
    headers = auth_headers(name="test_me_user", tier="premium")
    response = client.get("/api/v1/clients/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_me_user"
    assert data["tier"] == "premium"


def test_get_me_unauthenticated(client):
    response = client.get("/api/v1/clients/me")
    assert response.status_code == 401


def test_list_clients_admin_only(client, auth_headers):
    admin_headers = auth_headers(name="admin_user", tier="admin")
    response = client.get("/api/v1/clients", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    basic_headers = auth_headers(name="basic_user", tier="basic")
    forbidden_response = client.get("/api/v1/clients", headers=basic_headers)
    assert forbidden_response.status_code == 403

