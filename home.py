from flask import Flask, render_template_string, request, jsonify
from sqlalchemy import select, func
from models import db, Location

def load_html(path: str) -> str:
    with open(path) as file:
        return file.read()

HOME_HTML = load_html("home.html")

app = Flask(__name__, static_folder="static") #starts the app

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://maphole_user:securepasskey123@98.94.48.13:6543/maphole_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


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
    
#----------------------------------------------#

@app.route("/locations", methods=["GET"])
@app.route("/locations", methods=["GET"])
def get_locations():
    # Return id, lat, lon, created_at (simple to consume)
    rows = db.session.execute(
        select(
            Location.id,
            func.ST_Y(Location.geom).label("lat"),
            func.ST_X(Location.geom).label("lon"),
            Location.created_at
        ).order_by(Location.id)
    ).all()

    return jsonify([
        {
            "id": r.id,
            "lat": float(r.lat) if r.lat is not None else None,
            "lon": float(r.lon) if r.lon is not None else None,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in rows
    ])

@app.route("/locations", methods=["POST"])
def add_location():
    # Accepts lat/lon (either query params or JSON)
    data = request.get_json(silent=True) or {}
    lat = request.args.get("lat", data.get("lat"), type=float)
    lon = request.args.get("lon", data.get("lon"), type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Provide lat and lon (floats)."}), 400

    # Build geometry directly with PostGIS (no parsing headaches)
    geom = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)

    loc = Location(geom=geom)
    db.session.add(loc)
    db.session.commit()
    return jsonify({"message": "Location added", "id": loc.id}), 201
# ---------------------------------------------------------------


@app.route("/map")
def map_page():
    with open("map.html", "r", encoding="utf-8") as f:
        return render_template_string(f.read())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
