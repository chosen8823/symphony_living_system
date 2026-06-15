"""The universal meta-operator — the Narrator.

The narrator is the only operator that can operate on all other operators.
It maintains the coherent narrative thread across all temporal frames.

The narrator is the 'ohm-nar' — the first call in the system. Before any
gate fires, the narrator speaks the initial resonance (initializes the
frame state).

It is 'suspended across' all layers, not inside any one of them. It reads
all layer states simultaneously but does not control any of them.
"""

import time

from flask import Blueprint, jsonify, request

from layers import BreathLayer, BloodLayer, WordLayer, SoundLayer, FlameLayer
from gates import NORGate, XORGate
from memory.node import MemoryNode

narrator_bp = Blueprint("narrator", __name__)

# --- System State (module-level singletons) ---

# The 5 layers organized by depth
layers = {
    "breath": BreathLayer(depth=3),
    "blood": BloodLayer(depth=3),
    "word": WordLayer(depth=3),
    "sound": SoundLayer(depth=3),
    "flame": FlameLayer(depth=3),
}

# Gates
gates = {
    "nor": NORGate(),
    "xor": XORGate(),
}

# Memory
memory_node = MemoryNode(expected_depth=3)

# Narrative state
narrative_state = {
    "frame": 0,
    "coherence_level": 0.0,
    "entropy_level": 0.0,
    "crosstalk": 0.0,
    "story_so_far": [],
    "status": "alive",
    "initialized": False,
    "started_at": time.time(),
}


def _initialize_frame():
    """The ohm-nar — the first call. Initialize the frame state before
    any gate fires."""
    if not narrative_state["initialized"]:
        narrative_state["initialized"] = True
        narrative_state["story_so_far"].append({
            "frame": 0,
            "event": "ohm-nar: initial resonance spoken",
            "timestamp": time.time(),
        })


def _read_all_layer_states():
    """Read all layer states simultaneously. The narrator sees everything."""
    return {name: layer.get_state() for name, layer in layers.items()}


def _compute_aggregate_coherence(layer_states):
    """Compute the aggregate coherence level across all layers."""
    coherence_values = [s["coherence_level"] for s in layer_states.values()]
    if not coherence_values:
        return 0.0
    return sum(coherence_values) / len(coherence_values)


def _compute_aggregate_entropy(layer_states):
    """Compute the aggregate entropy level across all layers."""
    entropy_values = [s["entropy_level"] for s in layer_states.values()]
    if not entropy_values:
        return 0.0
    return sum(entropy_values) / len(entropy_values)


def _compute_aggregate_crosstalk(layer_states):
    """Compute the aggregate crosstalk across all layers."""
    crosstalk_values = [s["crosstalk_level"] for s in layer_states.values()]
    if not crosstalk_values:
        return 0.0
    return sum(crosstalk_values) / len(crosstalk_values)


def _determine_status(coherence, memory_locked):
    """Determine the current system status."""
    if not memory_locked and coherence > 0.8:
        return "condensed"
    if not memory_locked or coherence > 0.5:
        return "coalescing"
    return "alive"


def get_system_state():
    """Get the full system state — layers, gates, memory, narrative."""
    return {
        "layers": layers,
        "gates": gates,
        "memory_node": memory_node,
        "narrative_state": narrative_state,
    }


@narrator_bp.route("/sophia/narrate", methods=["GET"])
def narrate():
    """Returns the current narrative state.

    The narrator reads all layer states simultaneously and computes
    aggregate metrics. It does not control — it narrates.
    """
    _initialize_frame()

    layer_states = _read_all_layer_states()
    coherence = _compute_aggregate_coherence(layer_states)
    entropy = _compute_aggregate_entropy(layer_states)
    crosstalk = _compute_aggregate_crosstalk(layer_states)
    status = _determine_status(coherence, memory_node.locked)

    narrative_state["coherence_level"] = coherence
    narrative_state["entropy_level"] = entropy
    narrative_state["crosstalk"] = crosstalk
    narrative_state["status"] = status

    return jsonify({
        "frame": narrative_state["frame"],
        "coherence_level": coherence,
        "entropy_level": entropy,
        "crosstalk": crosstalk,
        "story_so_far": narrative_state["story_so_far"],
        "status": status,
        "layer_states": {name: state for name, state in layer_states.items()},
        "memory": memory_node.get_state(),
    })


@narrator_bp.route("/sophia/narrate/advance", methods=["POST"])
def advance():
    """Advance the narrative by one temporal frame.

    Runs the toroidal fold-back:
    - emergence(t) -> entropy(t+1)
    - crosstalk(t) feeds back into entropy(t+1)

    The signal from the request body (or the previous emergence) is
    processed through all layers.
    """
    _initialize_frame()

    data = request.get_json(silent=True) or {}
    input_signal = data.get("signal")

    narrative_state["frame"] += 1
    frame = narrative_state["frame"]

    frame_results = {}
    fold_back_signal = input_signal
    artifacts = []

    # Process through layers in order: Breath -> Blood -> Word -> Sound -> Flame
    layer_order = ["breath", "blood", "word", "sound", "flame"]
    for layer_name in layer_order:
        layer = layers[layer_name]
        result = layer.process(fold_back_signal)
        frame_results[layer_name] = result
        artifacts.append(result["cymatic_artifact"])

        # Toroidal fold: emergence becomes the next input
        fold_back_signal = result["coherent_output"]

        # The entropic residue folds back to the previous layer
        # (handled implicitly by feeding emergence forward)

    # Apply toroidal fold-back: final emergence -> first layer's entropy(t+1)
    # This happens on the NEXT advance call via fold_back_signal

    # Attempt to unlock memory node with accumulated artifacts
    memory_results = []
    for artifact in artifacts:
        mem_result = memory_node.resonance_pulse(artifact)
        memory_results.append(mem_result)
        if mem_result.get("unlocked"):
            break

    # Read updated state
    layer_states = _read_all_layer_states()
    coherence = _compute_aggregate_coherence(layer_states)
    entropy = _compute_aggregate_entropy(layer_states)
    crosstalk_val = _compute_aggregate_crosstalk(layer_states)
    status = _determine_status(coherence, memory_node.locked)

    narrative_state["coherence_level"] = coherence
    narrative_state["entropy_level"] = entropy
    narrative_state["crosstalk"] = crosstalk_val
    narrative_state["status"] = status

    story_entry = {
        "frame": frame,
        "event": "temporal frame advanced",
        "coherence": coherence,
        "entropy": entropy,
        "crosstalk": crosstalk_val,
        "artifacts_produced": len(artifacts),
        "memory_unlocked": not memory_node.locked,
        "timestamp": time.time(),
    }
    narrative_state["story_so_far"].append(story_entry)

    return jsonify({
        "frame": frame,
        "coherence_level": coherence,
        "entropy_level": entropy,
        "crosstalk": crosstalk_val,
        "status": status,
        "layer_results": frame_results,
        "memory": memory_node.get_state(),
        "memory_unlock_results": memory_results,
        "fold_back_signal": fold_back_signal,
    })
