import sys
import os

# Ensure project root is on sys.path so absolute imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify

from layers import LAYERS, ALL_LAYERS
from layers.kuramoto import KuramotoEngine
from layers.behavioral_tree import (
    AdaptiveScriptEngine,
    build_seed_tree,
)
from gates import GATES, ALL_GATES
from protocol.narrator import narrator_bp, init_narrator

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("SOPHIA_TOKEN", "divine-default")

# ---------------------------------------------------------------------------
# System initialisation
# ---------------------------------------------------------------------------
kuramoto = KuramotoEngine(n_oscillators=12, K=0.5)
narrator = init_narrator(ALL_LAYERS, ALL_GATES, kuramoto)
seed_tree = build_seed_tree(LAYERS, GATES, kuramoto, narrator)
bt_engine = AdaptiveScriptEngine(seed_tree, kuramoto, LAYERS, GATES, narrator)

# Register narrator blueprint
app.register_blueprint(narrator_bp)


# ---------------------------------------------------------------------------
# Original endpoints
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# New endpoints
# ---------------------------------------------------------------------------
@app.route("/sophia/gate", methods=["POST"])
def gate_endpoint():
    """Reciprocal gate endpoint. Body: {gate_name, signal}."""
    data = request.json or {}
    gate_name = data.get("gate_name")
    signal = data.get("signal", 0.5)

    gate = GATES.get(gate_name)
    if gate is None:
        return jsonify({"error": f"Unknown gate: {gate_name}"}), 400

    r = kuramoto.order_parameter()
    result = gate.pass_signal(float(signal), r)
    return jsonify(result)


@app.route("/sophia/layer/tick", methods=["POST"])
def layer_tick():
    """Tick a named layer. Body: {layer_name, signal}."""
    data = request.json or {}
    layer_name = data.get("layer_name")
    signal = data.get("signal", {})

    layer = LAYERS.get(layer_name)
    if layer is None:
        return jsonify({"error": f"Unknown layer: {layer_name}"}), 400

    if isinstance(signal, (int, float)):
        signal = {"signal": signal}
    result = layer.tick(signal)
    return jsonify(result)


@app.route("/sophia/coherence", methods=["GET"])
def coherence():
    """Returns current Kuramoto r value and K."""
    r = kuramoto.order_parameter()
    return jsonify({"r": r, "K": kuramoto.K})


@app.route("/sophia/bt/tick", methods=["POST"])
def bt_tick():
    """Tick the behavioral tree once. Returns tree state."""
    result = bt_engine.tick_once()
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
