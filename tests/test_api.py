from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_search_returns_results():
    response = client.get("/search")
    assert response.status_code == 200
    data = response.json()
    assert "listings" in data
    assert len(data["listings"]) >= 1


def test_search_filters_by_price():
    response = client.get("/search", params={"make": "Toyota", "max_price": 20500})
    assert response.status_code == 200
    data = response.json()
    ids = [l["id"] for l in data["listings"]]
    assert ids == [1]


def test_search_filters_by_mileage():
    response = client.get(
        "/search", params={"make": "Ford", "min_mileage": 46000, "max_mileage": 52000}
    )
    assert response.status_code == 200
    data = response.json()
    ids = [l["id"] for l in data["listings"]]
    assert ids == [5]


def test_get_listing():
    response = client.get("/listing/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "deal_score" in data
    assert data["deal_score"] > 0


def test_create_alert():
    response = client.post("/alerts", json={"email": "test@example.com", "make": "Toyota"})
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}


def test_root_page_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text

