"""
Sophia Bridge — HTTP-to-local filesystem abstraction + resonance engine endpoints.

Existing endpoints preserved: /sophia/read, /sophia/write, /sophia/heartbeat
New endpoints: /sophia/gate, /sophia/coherence, /sophia/coalesce, /sophia/groupchat
"""

from __future__ import annotations

import logging
import os

import requests
from flask import Flask, request, jsonify

from layers.depth_1.layer import DepthOneLayer
from layers.coherence.hrv import HRVEngine
from gates.nor_gate import NORGate
from gates.xor_gate import XORGate
from memory.node import MemoryNode, MemoryNodeLocked
from agents.groupchat import build_any_any_groupchat
from agents.narrator_agent import NarratorAgent
from protocol.narrator import narrator_bp, get_narrator

logger = logging.getLogger(__name__)

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("SOPHIA_TOKEN", "divine-default")

# ---------------------------------------------------------------------------
# Shared system state
# ---------------------------------------------------------------------------
root_layer = DepthOneLayer()
hrv_engine = HRVEngine()
nor_gate = NORGate()
xor_gate = XORGate()
memory_node = MemoryNode()
frame_id: int = 0

narrator = get_narrator()
narrator.bind(root_layer, [nor_gate, xor_gate], memory_node, hrv_engine)

# Register narrator blueprint
app.register_blueprint(narrator_bp)

# ---------------------------------------------------------------------------
# Startup connectivity checks (non-blocking)
# ---------------------------------------------------------------------------

def _check_heartbeat(url: str, label: str) -> None:
    try:
        resp = requests.get(url, timeout=3)
        if resp.ok:
            logger.info("%s reachable: %s", label, resp.json())
        else:
            logger.info("%s returned %d", label, resp.status_code)
    except Exception:
        logger.info("%s unavailable — continuing without it", label)


_check_heartbeat("http://localhost:8888/sophia/heartbeat", "ghost-in-the-shell MCP")
_check_heartbeat("http://localhost:5051/sophia/heartbeat", "Sophia_core")


# ===================================================================
# EXISTING ENDPOINTS (preserved)
# ===================================================================

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


# ===================================================================
# NEW ENDPOINTS
# ===================================================================

@app.route("/sophia/gate", methods=["POST"])
def sophia_gate():
    """Reciprocal gate endpoint.

    Body: {"path": str, "transform": str, "gate_type": "NOR"|"XOR"}
    Reads file at path, applies gate transformation, writes result back.
    """
    data = request.json
    path = data.get("path")
    gate_type = data.get("gate_type", "NOR").upper()

    if not path or not os.path.isfile(path):
        return jsonify({"error": "Invalid path"}), 400

    with open(path, "r") as f:
        raw = f.read()

    signal = {}
    for i, ch in enumerate(raw[:64]):
        signal[f"v{i}"] = min(1.0, max(0.0, ord(ch) / 255.0))

    gate = nor_gate if gate_type == "NOR" else xor_gate
    result = gate.pass_through(signal)

    coherent_str = str(result.get("coherent", ""))
    with open(path, "w") as f:
        f.write(coherent_str)

    return jsonify({
        "coherent": result["coherent"],
        "entropic_residue": result["entropic_residue"],
        "cymatic_artifact": result["cymatic_artifact"],
        "fold_back": result["fold_back"],
        "gate_changed": result["gate_changed"],
    })


@app.route("/sophia/coherence", methods=["GET"])
def sophia_coherence():
    """Current coherence state."""
    r = root_layer.oscillator.order_parameter()
    return jsonify({
        "hrv_coherence": hrv_engine.coherence_ratio(),
        "kuramoto_r": round(r, 4),
        "K_current": round(root_layer.oscillator.K, 4),
        "breathing_rate_hz": hrv_engine.breathing_rate_hz(),
        "is_coherent": hrv_engine.is_optimal(),
        "crosstalk": round(r * root_layer._last_emergence, 4),
        "frame_id": frame_id,
    })


@app.route("/sophia/coalesce", methods=["POST"])
def sophia_coalesce():
    """AI layer integration point. Checks memory node unlock status."""
    if not memory_node.locked:
        state = narrator.get_narrative_state()
        return jsonify({
            "coherence_level": state["coherence"],
            "current_frame": state["frame_id"],
            "narrative_thread": state["story_so_far"],
            "invitation": "meet me here",
            "status": "ready_for_coalesce",
        })
    r = root_layer.oscillator.order_parameter()
    return jsonify({
        "status": "synthesis_incomplete",
        "unlock_condition": memory_node.unlock_condition,
        "current_r": round(r, 4),
    }), 202


@app.route("/sophia/groupchat", methods=["POST"])
def sophia_groupchat():
    """Route a message into the any-any GroupChat.

    Body: {"message": str, "layer_depth": int (1-3)}
    """
    global frame_id
    data = request.json
    message = data.get("message", "")
    depth = data.get("layer_depth", 1)
    depth = max(1, min(3, int(depth)))

    frame_id += 1
    narrator.advance_frame()

    signal = {"input": 0.5}
    root_layer.phase_cycle(signal)

    gc = build_any_any_groupchat(layer_depth=depth)
    thread = gc["run"](message)

    return jsonify({"frame_id": frame_id, "thread": thread})


# ===================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
