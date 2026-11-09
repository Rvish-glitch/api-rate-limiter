def test_routes_crud_admin(client, auth_headers):
    admin_headers = auth_headers(name="super_admin", tier="admin")

    # Create Route
    create_res = client.post(
        "/api/v1/routes",
        json={"path": "/v1/users", "destination_url": "http://user-service:8080", "is_active": True},
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    route_id = create_res.json()["id"]

    # List Routes
    list_res = client.get("/api/v1/routes", headers=admin_headers)
    assert list_res.status_code == 200
    assert any(r["id"] == route_id for r in list_res.json())

    # Delete Route
    del_res = client.delete(f"/api/v1/routes/{route_id}", headers=admin_headers)
    assert del_res.status_code == 204

