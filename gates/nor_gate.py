"""NOR gate — the void state gate.

Neither signal nor noise. Used at the boundary between temporal frames.
When both inputs are zero/null, it outputs the void state which unlocks
the memory node.
"""

from gates.base_gate import BaseGate


class NORGate(BaseGate):
    """Void state gate operating on gradients, not strict booleans.

    The NOR gate produces maximum output when both inputs approach zero.
    This is the boundary condition — the silence between frames — where
    the memory node can be unlocked.
    """

    def __init__(self):
        super().__init__(name="NOR")
        self.void_threshold = 0.1  # Below this, both inputs are "near-zero"

    def _apply_transform(self, signal, current_state):
        """NOR transformation: outputs void state when inputs approach zero.

        Uses gradient logic — not strict boolean. Values near zero produce
        high output; values far from zero produce low output.
        """
        if isinstance(signal, (int, float)):
            input_a = float(signal)
            input_b = current_state.get("resonance", 0.0)
        elif isinstance(signal, dict):
            input_a = float(signal.get("a", 0.0))
            input_b = float(signal.get("b", current_state.get("resonance", 0.0)))
        else:
            input_a = 0.0
            input_b = 0.0

        # Gradient NOR: output is high when both inputs are low
        nor_output = max(0.0, 1.0 - max(abs(input_a), abs(input_b)))

        is_void = abs(input_a) < self.void_threshold and abs(input_b) < self.void_threshold

        # When in void state, the gate becomes maximally transparent
        if is_void:
            transmitted = 1.0  # Void opens the gate fully
            reflected = 0.0
        else:
            transmitted = nor_output * (1.0 - current_state["reflection_ratio"])
            reflected = nor_output * current_state["reflection_ratio"]

        # Signal still changes the gate (reciprocal)
        new_state = {
            "resonance": (current_state["resonance"] + nor_output) / 2.0,
            "absorption": min(current_state["absorption"] + 0.005, 1.0),
            "reflection_ratio": current_state["reflection_ratio"] * 0.95 if is_void else current_state["reflection_ratio"],
            "transmutation_count": current_state["transmutation_count"] + 1,
            "last_signal": signal,
            "gate_modified": True,
            "void_state": is_void,
            "nor_output": nor_output,
        }

        return transmitted, reflected, new_state

    def is_void(self):
        """Check if the gate is currently in the void state."""
        return self.state.get("void_state", False)
