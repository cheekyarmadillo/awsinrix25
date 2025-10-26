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

    # List
    r = client.get("/model")
    assert r.status_code == 200
    rows = r.get_json()
    assert isinstance(rows, list)
    # Ensure at least the last two are present somewhere in the list
    lats = [row["lat"] for row in rows]
    lons = [row["lon"] for row in rows]
    assert any(approx_eq(lat, p1["lat"]) for lat in lats)
    assert any(approx_eq(lon, p1["lon"]) for lon in lons)
    assert any(approx_eq(lat, p2["lat"]) for lat in lats)
    assert any(approx_eq(lon, p2["lon"]) for lon in lons)

def test_parse_point_wkt_helper_import(client):
    """
    Validate the private WKT parser on a couple of edge cases.
    """
    import home

    # Good WKT
    lat, lon = home._parse_point_wkt("POINT(-122.0840575 37.4219999)")
    assert approx_eq(lat, 37.4219999)
    assert approx_eq(lon, -122.0840575)

    # Bad WKT shapes
    lat, lon = home._parse_point_wkt("LINESTRING(0 0, 1 1)")
    assert lat is None and lon is None

    lat, lon = home._parse_point_wkt("POINT(invalid tokens)")
    assert lat is None and lon is None
