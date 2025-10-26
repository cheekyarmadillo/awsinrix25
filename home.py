from flask import Flask, render_template_string, request, jsonify

def load_html(path: str) -> str:
    with open(path) as file:
        return file.read()

HOME_HTML = load_html("home.html")

app = Flask(__name__, static_folder="static") #starts the app

@app.route("/process", methods=["POSTS"])
def get_js_data():
    data = request.get_json()
    
    return jsonify(result=data)

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
