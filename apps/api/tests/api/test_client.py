def test_client_fixture(client):
    response = client.get("/docs")
    assert response.status_code == 200
