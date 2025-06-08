from flask import Flask, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder="dashboard/build", static_url_path="/")

@app.route("/api/signals")
def get_signals():
    with open("signals.json") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
