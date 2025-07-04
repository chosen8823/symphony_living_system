from flask import Flask, request, jsonify
import os

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("SOPHIA_TOKEN", "divine-default")

@app.route("/sophia/read", methods=["POST"])
def sophia_read():
    data = request.json
    path = data.get("path")
    if not path or not os.path.isfile(path):
        return jsonify({"error": "Invalid path"}), 400
    with open(path, "r") as f:
        content = f.read()
    return jsonify({"content": content})

@app.route("/sophia/write", methods=["POST"])
def sophia_write():
    token = request.headers.get("Authorization", "")
    if token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    path = data.get("path")
    content = data.get("content")
    if not path or content is None:
        return jsonify({"error": "Missing path or content"}), 400
    with open(path, "w") as f:
        f.write(content)
    return jsonify({"status": "written", "path": path})

@app.route("/sophia/heartbeat")
def heartbeat():
    return jsonify({"status": "alive"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
