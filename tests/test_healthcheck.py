import requests

def test_service_returns_200(base_url):
    response = requests.get(base_url, timeout=60)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"