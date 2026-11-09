def test_rate_limit_headers_present(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_rate_limit_status_endpoint(client, auth_headers):
    headers = auth_headers(name="rate_user", tier="basic")
    response = client.get("/api/v1/rate-limits/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["client_name"] == "rate_user"
    assert data["tier"] == "basic"
    assert "limit" in data
    assert "remaining" in data

