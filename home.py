import os
from flask import Flask, render_template_string, request, jsonify
from sqlalchemy import text
from geoalchemy2 import WKTElement

from models import db, Location


def load_html(path: str) -> str:
    with open(path) as file:
        return file.read()


HOME_HTML = load_html("home.html")

# Configuration
# Allow overriding via environment for deployment; fall back to the provided EC2/Postgres URL
DEFAULT_DATABASE_URL = "postgresql://maphole_user:securepasskey123@98.94.48.13:5432/maphole_db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)

app = Flask(__name__, static_folder="static")
app.config.setdefault("SQLALCHEMY_DATABASE_URI", DATABASE_URL)
app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

# initialize SQLAlchemy from models.py
db.init_app(app)

# Server host/port - enable binding to 0.0.0.0 for EC2 deployment. Can be overridden by env vars.
SERVER_HOST = os.environ.get("HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("PORT", 5000))


@app.route("/process", methods=["POST"])
def get_js_data():
    data = request.get_json()
    print(data.get("imageName"))
    return jsonify(result=data)


@app.route("/")
def home():
    return render_template_string(HOME_HTML)


@app.route("/report")
def report():
    with open("report.html", "r", encoding="utf-8") as file:
        return render_template_string(file.read())


def _parse_point_wkt(wkt: str):
    # expects 'POINT(lon lat)'
    if not wkt or not wkt.startswith("POINT"):
        return None, None
    inside = wkt[wkt.find("(") + 1:wkt.find(")")]
    try:
        lon_str, lat_str = inside.strip().split()
        return float(lat_str), float(lon_str)  # return as (lat, lon)
    except Exception:
        return None, None


@app.route("/db/init", methods=["POST"])
def db_init():
    """Create tables. POST only - call once after configuring DB."""
    with app.app_context():
        db.create_all()
    return jsonify(status="ok", message="tables created")


@app.route("/health", methods=["GET"])
def health_check():
    """Basic health check: returns app status and tries a simple DB query."""
    db_ok = False
    db_error = None
    try:
        with app.app_context():
            # quick sanity query
            res = db.session.execute(text("SELECT 1")).fetchone()
            db_ok = bool(res)
    except Exception as exc:
        db_error = str(exc)

    return jsonify(app="ok", db_ok=db_ok, db_error=db_error)


@app.route("/model", methods=["POST"])
def create_location():
    """Create a new Location row. JSON: {name, description, lat, lon}"""
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description")
    lat = data.get("lat")
    lon = data.get("lon")
    if not name or lat is None or lon is None:
        return jsonify(error="missing name/lat/lon"), 400

    try:
        geom = WKTElement(f"POINT({lon} {lat})", srid=4326)
        location = Location(name=name, description=description, geom=geom)
        with app.app_context():
            db.session.add(location)
            db.session.commit()
            loc_id = location.id
        return jsonify(id=loc_id, name=name), 201
    except Exception as exc:
        return jsonify(error=str(exc)), 500


@app.route("/model/<int:loc_id>", methods=["GET"])
def get_location(loc_id: int):
    """Return a single location as JSON."""
    # Use ST_AsText to get the POINT text
    stmt = text(
        "SELECT id, name, description, created_at, ST_AsText(geom) AS wkt FROM locations WHERE id = :id"
    )
    result = None
    with app.app_context():
        res = db.session.execute(stmt, {"id": loc_id}).fetchone()
        if not res:
            return jsonify(error="not found"), 404
        wkt = res["wkt"] if isinstance(res, dict) else res[4]
        lat, lon = _parse_point_wkt(wkt)
        result = {
            "id": res[0] if not isinstance(res, dict) else res.get("id"),
            "name": res[1] if not isinstance(res, dict) else res.get("name"),
            "description": res[2] if not isinstance(res, dict) else res.get("description"),
            "created_at": str(res[3]) if not isinstance(res, dict) else str(res.get("created_at")),
            "lat": lat,
            "lon": lon,
        }
    return jsonify(result)


@app.route("/model", methods=["GET"])
def list_locations():
    """List locations (limit 100)."""
    stmt = text(
        "SELECT id, name, description, created_at, ST_AsText(geom) AS wkt FROM locations ORDER BY id DESC LIMIT 100"
    )
    rows = []
    with app.app_context():
        res = db.session.execute(stmt).fetchall()
        for r in res:
            wkt = r[4]
            lat, lon = _parse_point_wkt(wkt)
            rows.append({
                "id": r[0],
                "name": r[1],
                "description": r[2],
                "created_at": str(r[3]),
                "lat": lat,
                "lon": lon,
            })
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
