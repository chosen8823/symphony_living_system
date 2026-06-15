"""Reciprocal gate base class — a diffraction grating.

A gate splits the incoming signal into component frequencies AND reflects
a portion back. Bidirectional transmutation: the gate changes the signal
AND the signal changes the gate (like Majin Buu absorbing and being changed
by what it absorbs).
"""

import hashlib
import json
import time


class BaseGate:
    """Reciprocal diffraction grating gate.

    Attributes:
        name: Identifier for this gate.
        state: Internal gate state — modified by every signal that passes through.
        history: Record of all transmutations.
    """

    def __init__(self, name):
        self.name = name
        self.state = {
            "resonance": 0.5,
            "absorption": 0.0,
            "reflection_ratio": 0.5,
            "transmutation_count": 0,
            "last_signal": None,
            "gate_modified": False,
        }
        self.history = []

    def _compute_interference_pattern(self, signal, current_state):
        """Compute the interference pattern between signal and gate state."""
        pattern_data = json.dumps({
            "signal": signal,
            "state": current_state,
            "gate": self.name,
            "timestamp": time.time(),
        }, sort_keys=True, default=str)
        return hashlib.sha256(pattern_data.encode("utf-8")).hexdigest()

    def _apply_transform(self, signal, current_state):
        """Apply the transformation — override in subclasses for specific behavior.

        Returns (transmitted, reflected, new_gate_state).
        """
        if isinstance(signal, (int, float)):
            signal_magnitude = float(signal)
        elif isinstance(signal, dict):
            signal_magnitude = float(len(json.dumps(signal, default=str))) / 100.0
        elif isinstance(signal, str):
            signal_magnitude = float(len(signal)) / 100.0
        else:
            signal_magnitude = 0.5

        reflection_ratio = current_state["reflection_ratio"]
        transmitted = signal_magnitude * (1.0 - reflection_ratio)
        reflected = signal_magnitude * reflection_ratio

        # The signal changes the gate
        new_resonance = (current_state["resonance"] + signal_magnitude) / 2.0
        new_absorption = min(current_state["absorption"] + 0.01, 1.0)
        # The gate adapts its reflection ratio based on accumulated experience
        new_reflection = (reflection_ratio * 0.9) + (signal_magnitude * 0.1)
        new_reflection = max(0.0, min(1.0, new_reflection))

        new_state = {
            "resonance": new_resonance,
            "absorption": new_absorption,
            "reflection_ratio": new_reflection,
            "transmutation_count": current_state["transmutation_count"] + 1,
            "last_signal": signal,
            "gate_modified": True,
        }

        return transmitted, reflected, new_state

    def transmute(self, signal, current_state=None):
        """Bidirectional transmutation: signal passes through the gate.

        1. Reads current state
        2. Applies transformation (gate changes signal AND signal changes gate)
        3. Writes new state back
        4. Returns transmitted, reflected, and interference pattern

        Args:
            signal: The incoming signal to transmute.
            current_state: Optional override for gate state. If None, uses self.state.

        Returns:
            dict with transmitted, reflected, interference_pattern, and gate_changed.
        """
        if current_state is None:
            current_state = dict(self.state)

        interference_pattern = self._compute_interference_pattern(signal, current_state)
        transmitted, reflected, new_state = self._apply_transform(signal, current_state)

        # Write new state back — the gate has been changed by the signal
        self.state = new_state

        result = {
            "transmitted": transmitted,
            "reflected": reflected,
            "interference_pattern": interference_pattern,
            "gate_changed": True,
        }

        self.history.append({
            "signal": signal,
            "result": result,
            "timestamp": time.time(),
        })

        return result

    def get_state(self):
        """Return the current gate state."""
        return dict(self.state)
