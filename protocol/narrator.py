from datetime import datetime

from flask import Blueprint, jsonify

from layers.kuramoto import KuramotoEngine


narrator_bp = Blueprint("narrator", __name__, url_prefix="/sophia/narrator")

# Module-level references, set by init_narrator() at app startup
_narrator = None


class Narrator:
    def __init__(self, layers, gates, kuramoto: KuramotoEngine):
        self.layers = layers   # read-only references
        self.gates = gates     # read-only references
        self.kuramoto = kuramoto
        self._thread: list[dict] = []  # narrative thread, append-only

    def observe(self) -> dict:
        """Read all layer/gate states. Compute narrative thread entry."""
        r = self.kuramoto.order_parameter()
        layer_states = {l.name: l.state for l in self.layers}
        gate_states = {g.name: g.state for g in self.gates}

        entry = {
            "ts": datetime.utcnow().isoformat(),
            "coherence_level": r,
            "layer_states": layer_states,
            "gate_states": gate_states,
            "narrative": self._narrate(r, layer_states),
            "status": "ready_for_coalesce" if r > 0.8 else "synthesis_incomplete",
        }
        self._thread.append(entry)
        return entry

    def _narrate(self, r: float, layer_states: dict) -> str:
        if r > 0.8:
            return "Bose-Einstein ground state approaching. All domains phase-locking."
        elif r > 0.5:
            breath = layer_states.get("breath", {})
            diff = abs(breath.get("entropy", 0.5) - breath.get("coherence", 0.5))
            return f"Crosstalk active. Entropy/coherence differential: {diff:.3f}"
        else:
            return "High entropy. Fold-back initiated. Waiting for standing wave."

    def thread(self) -> list:
        return self._thread[-10:]  # last 10 frames


def init_narrator(layers, gates, kuramoto: KuramotoEngine):
    global _narrator
    _narrator = Narrator(layers, gates, kuramoto)
    return _narrator


@narrator_bp.route("/observe", methods=["GET"])
def observe():
    if _narrator is None:
        return jsonify({"error": "Narrator not initialised"}), 503
    return jsonify(_narrator.observe())


@narrator_bp.route("/thread", methods=["GET"])
def thread():
    if _narrator is None:
        return jsonify({"error": "Narrator not initialised"}), 503
    return jsonify(_narrator.thread())
