import os
import hmac
import hashlib

import numpy as np


class BaseGate:
    def __init__(self, name: str, gate_type: str = "NOR"):
        self.name = name
        self.gate_type = gate_type  # "NOR" or "XOR"
        self.state = 0.5  # gradient, not boolean
        self._connections: list["BaseGate"] = []  # up to 12 (dodecahedral topology)

    def pass_signal(self, signal: float, parent_coherence: float) -> dict:
        """Reciprocal: signal changes gate, gate changes signal."""
        if self.gate_type == "NOR":
            output = float(np.clip(1.0 - max(signal, self.state), 0, 1))
        elif self.gate_type == "XOR":
            output = float(np.clip(abs(signal - self.state), 0, 1))
        else:
            output = float(np.clip(signal * self.state, 0, 1))

        # gate state is updated by the signal (bidirectional transmutation)
        self.state = float(np.clip((self.state + signal) / 2, 0, 1))

        entropic_residue = float(np.clip(1.0 - output, 0, 1))
        cymatic = self._fingerprint(signal, output)

        return {
            "gate": self.name,
            "type": self.gate_type,
            "coherent": output,
            "entropic_residue": entropic_residue,
            "cymatic_artifact": cymatic,
            "fold_back": entropic_residue,  # residue re-enters at previous layer
        }

    def connect(self, other: "BaseGate"):
        if len(self._connections) < 12:  # dodecahedral max
            self._connections.append(other)

    def _fingerprint(self, signal: float, output: float) -> str:
        token = os.environ.get("SOPHIA_TOKEN", "divine-default")
        payload = f"{self.name}:{signal:.4f}:{output:.4f}:{self.state:.4f}"
        return hmac.new(
            token.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()[:16]
