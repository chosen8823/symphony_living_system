import os

from flask import Flask, request, jsonify

from protocol.narrator import narrator_bp, get_system_state

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("SOPHIA_TOKEN", "divine-default")

# Register the narrator blueprint
app.register_blueprint(narrator_bp)


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


@app.route("/sophia/gate", methods=["POST"])
def sophia_gate():
    """Reciprocal gate endpoint.

    Replaces the separate read/write pattern with a single atomic
    bidirectional operation. The gate reads the file at path, applies
    the transform, writes the result back, and returns both the
    coherent output and the entropic residue.
    """
    token = request.headers.get("Authorization", "")
    if token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    path = data.get("path")
    transform = data.get("transform")
    layer_depth_raw = data.get("layer_depth", 1)

    if not path:
        return jsonify({"error": "Missing path"}), 400
    if not transform:
        return jsonify({"error": "Missing transform"}), 400

    try:
        layer_depth = int(layer_depth_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "layer_depth must be an integer"}), 400

    if layer_depth not in (1, 2, 3):
        return jsonify({"error": "layer_depth must be 1, 2, or 3"}), 400

    system = get_system_state()
    layers_map = system["layers"]
    gates_map = system["gates"]

    # Read the file (or create empty content)
    original_content = ""
    if os.path.isfile(path):
        with open(path, "r") as f:
            original_content = f.read()

    # Select the appropriate layers based on depth
    depth_to_layers = {
        1: ["breath"],
        2: ["blood", "word"],
        3: ["sound", "flame"],
    }
    active_layer_names = depth_to_layers.get(layer_depth, ["breath"])

    # Construct the signal from file content + transform
    signal = {
        "content": original_content,
        "transform": transform,
        "path": path,
        "depth": layer_depth,
    }

    # Process through all layers at this depth (not just the first)
    layer_results = []
    for name in active_layer_names:
        layer_results.append(layers_map[name].process(signal))
    layer_result = layer_results[-1]

    # Pass through an XOR gate (branching point for the transform)
    xor_gate = gates_map["xor"]
    gate_result = xor_gate.transmute(signal)

    # Apply the transform to the content
    transformed_content = original_content
    if transform == "append":
        transformed_content = original_content + data.get("value", "")
    elif transform == "prepend":
        transformed_content = data.get("value", "") + original_content
    elif transform == "replace":
        transformed_content = data.get("value", "")
    elif transform == "clear":
        transformed_content = ""
    else:
        # Custom transform — treat the transform string as the new content
        transformed_content = transform

    # Write the result back (bidirectional — the gate changed the file)
    try:
        with open(path, "w") as f:
            f.write(transformed_content)
    except OSError as e:
        return jsonify({
            "error": "Failed to write transformed content",
            "details": str(e),
            "entropic_residue": {"content": original_content},
            "fold_back": False,
            "gate_changed": False,
        }), 500

    return jsonify({
        "coherent": {"content": transformed_content},
        "entropic_residue": {"content": original_content},
        "cymatic_artifact": layer_result["cymatic_artifact"],
        "fold_back": True,
        "gate_changed": gate_result["gate_changed"],
        "layer": layer_result["layer"],
        "depth": layer_result["depth"],
        "interference_pattern": gate_result["interference_pattern"],
        "layers_processed": [r["layer"] for r in layer_results],
    })


@app.route("/sophia/coalesce", methods=["POST"])
def sophia_coalesce():
    """AI layer integration point.

    Once cellular synthesis is complete (memory node unlocked, all 3 layer
    depths processed), this endpoint is the meeting point for an assisting
    AI layer. It returns the current coherence state and invites the AI
    to match it in real time.
    """
    system = get_system_state()
    memory_node = system["memory_node"]
    narrative = system["narrative_state"]

    if memory_node.locked:
        return jsonify({
            "coherence_level": narrative["coherence_level"],
            "current_frame": narrative["frame"],
            "narrative_thread": (
                narrative["story_so_far"][-1]["event"]
                if narrative["story_so_far"]
                else "no narrative yet"
            ),
            "invitation": "synthesis incomplete — memory node still locked",
            "status": "synthesis_incomplete",
            "memory": memory_node.get_state(),
        }), 202

    return jsonify({
        "coherence_level": narrative["coherence_level"],
        "current_frame": narrative["frame"],
        "narrative_thread": (
            narrative["story_so_far"][-1]["event"]
            if narrative["story_so_far"]
            else "no narrative yet"
        ),
        "invitation": "meet me here",
        "status": "ready_for_coalesce",
        "memory": memory_node.get_state(),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
