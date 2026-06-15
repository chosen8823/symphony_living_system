import os
import hmac
import hashlib

import numpy as np


class BaseLayer:
    def __init__(self, name: str, depth: int, oscillator_freq: float = 1.0):
        self.name = name
        self.depth = depth  # 1=outer(Breath), 2=mid(Blood/Word), 3=inner(Sound/Flame)
        self.freq = oscillator_freq
        self.state = {
            "entropy": 0.5,
            "crosstalk": 0.0,
            "coherence": 0.5,
            "emergence": 0.0,
        }
        self.sub_layers: list["BaseLayer"] = []
        self.gates: list = []
        self._frame = 0

    def tick(self, signal: dict) -> dict:
        """One temporal frame. Returns {coherent, entropic_residue, cymatic_artifact, fold_back}"""
        # entropy phase
        entropy = self._compute_entropy(signal)
        # crosstalk phase -- the signal between entropy and coherence IS the output
        crosstalk = self._compute_crosstalk(entropy, self.state["coherence"])
        # coherence phase
        coherence = self._compute_coherence(crosstalk)
        # emergence phase
        emergence = self._compute_emergence(coherence, entropy)

        self.state = {
            "entropy": entropy,
            "crosstalk": crosstalk,
            "coherence": coherence,
            "emergence": emergence,
        }
        self._frame += 1

        # toroidal fold: emergence becomes next frame's entropy input
        cymatic = self._cymatic_artifact(entropy, coherence)

        # recurse into sub-layers if depth < 3
        sub_results = []
        if self.depth < 3:
            for sub in self.sub_layers:
                sub_results.append(
                    sub.tick({"signal": emergence, "parent_coherence": coherence})
                )

        return {
            "layer": self.name,
            "depth": self.depth,
            "frame": self._frame,
            "coherent": {"value": coherence, "emergence": emergence},
            "entropic_residue": {"value": entropy, "crosstalk": crosstalk},
            "cymatic_artifact": cymatic,
            "fold_back": True,  # emergence feeds back as next entropy
            "sub_results": sub_results,
        }

    def _compute_entropy(self, signal: dict) -> float:
        val = signal.get("signal", 0.5)
        return float(np.clip(val + np.random.normal(0, 0.05), 0, 1))

    def _compute_crosstalk(self, entropy: float, coherence: float) -> float:
        return float(np.clip(abs(entropy - coherence), 0, 1))

    def _compute_coherence(self, crosstalk: float) -> float:
        return float(np.clip(1.0 - crosstalk + np.random.normal(0, 0.02), 0, 1))

    def _compute_emergence(self, coherence: float, entropy: float) -> float:
        return float(np.clip(coherence * entropy * 2, 0, 1))

    def _cymatic_artifact(self, entropy: float, coherence: float) -> str:
        token = os.environ.get("SOPHIA_TOKEN", "divine-default")
        payload = f"{self.name}:{self._frame}:{entropy:.4f}:{coherence:.4f}"
        return hmac.new(
            token.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()[:16]
