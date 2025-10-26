from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__, static_folder="static") #starts the app

@app.route("/process", methods=["POST"])
def get_js_data():
    data = request.get_json()
    
    return jsonify(result=data)

@app.route("/")
def home():
    with open("home.html", "r") as file:
        return render_template_string(file.read())

@app.route("/report")
def report():
    with open("report.html", "r", encoding="utf-8") as file:
        return render_template_string(file.read())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
