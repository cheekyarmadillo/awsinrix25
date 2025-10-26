import math
from sqlalchemy import text
import pytest

# A small helper for float comparisons
def approx_eq(a, b, tol=1e-7):
    return a is None or b is None or math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)

def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["app"] == "ok"
    assert data["db_ok"] is True, f"DB not OK: {data.get('db_error')}"

def test_create_and_get_location_roundtrip(client):
    # Create a point
    payload = {"lat": 37.4219999, "lon": -122.0840575}
    r = client.post("/model", json=payload)
    assert r.status_code == 201, r.get_data(as_text=True)
    created = r.get_json()
    loc_id = created["id"]
    assert isinstance(loc_id, int)
    assert approx_eq(created["lat"], payload["lat"])
    assert approx_eq(created["lon"], payload["lon"])
    assert "created_at" in created

    # Retrieve by id
    r2 = client.get(f"/model/{loc_id}")
    assert r2.status_code == 200, r2.get_data(as_text=True)
    got = r2.get_json()["result"]
    assert got["id"] == loc_id
    assert approx_eq(got["lat"], payload["lat"])
    assert approx_eq(got["lon"], payload["lon"])
    assert "created_at" in got

def test_list_locations_contains_created_point(client):
    # Create two points
    p1 = {"lat": 40.0, "lon": -120.0}
    p2 = {"lat": 41.5, "lon": -121.75}
    r1 = client.post("/model", json=p1)
    r2 = client.post("/model", json=p2)
    assert r1.status_code == 201
    assert r2.status_code == 201