from flask import Flask, render_template_string, request, jsonify
import os

def load_html(path: str) -> str:
    with open(path) as file:
        return file.read()

HOME_HTML = load_html("home.html")
REPORT_HTML = load_html("report.html")
MAP_HTML = load_html("map.html")

app = Flask(__name__, static_folder="static") #starts the app

@app.route("/process", methods=["POST"])
def get_js_data():
    data = request.get_json()
    print(data.get("imageName"));
    print(os.path.exists(data.get("imageName")))
    
    return jsonify(result=data)

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/report")
def report():
    return render_template_string(REPORT_HTML)

@app.route("/map")
def map_page():
    return render_template_string(MAP_HTML)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
