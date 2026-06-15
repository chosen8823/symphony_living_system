"""XOR gate — the branching point gate.

Exclusive divergence. Used where the path splits into parallel processes.
The 'buuleanian' operator for creating new branches. Operates on gradients,
not strict booleans.
"""

from gates.base_gate import BaseGate


class XORGate(BaseGate):
    """Branching point gate using gradient XOR logic.

    The XOR gate produces maximum output when inputs diverge (one high,
    one low). This is the branching condition — where a single path
    splits into parallel processes.
    """

    def __init__(self):
        super().__init__(name="XOR")

    def _apply_transform(self, signal, current_state):
        """XOR transformation: outputs high when inputs diverge.

        Uses gradient logic — values are treated as continuous, not binary.
        Maximum output when one input is high and the other is low.
        """
        if isinstance(signal, (int, float)):
            input_a = float(signal)
            input_b = current_state.get("resonance", 0.5)
        elif isinstance(signal, dict):
            input_a = float(signal.get("a", 0.0))
            input_b = float(signal.get("b", current_state.get("resonance", 0.5)))
        else:
            input_a = 0.5
            input_b = 0.5

        # Gradient XOR: maximum when inputs are maximally different
        xor_output = abs(input_a - input_b)

        # The branching ratio determines how the signal splits
        branch_ratio = xor_output
        transmitted = xor_output * (1.0 - current_state["reflection_ratio"])
        reflected = xor_output * current_state["reflection_ratio"]

        # When divergence is high, the gate creates a new branch
        is_branching = xor_output > 0.5

        new_state = {
            "resonance": (current_state["resonance"] + xor_output) / 2.0,
            "absorption": min(current_state["absorption"] + 0.01, 1.0),
            "reflection_ratio": (current_state["reflection_ratio"] + branch_ratio) / 2.0,
            "transmutation_count": current_state["transmutation_count"] + 1,
            "last_signal": signal,
            "gate_modified": True,
            "branching": is_branching,
            "branch_ratio": branch_ratio,
            "xor_output": xor_output,
        }

        return transmitted, reflected, new_state

    def is_branching(self):
        """Check if the gate is currently in a branching state."""
        return self.state.get("branching", False)
