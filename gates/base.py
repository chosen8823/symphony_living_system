"""
BaseGate — monadic Merkaba reciprocal gate.

Each gate is a diffraction grating: splits incoming signal into
coherent + entropic_residue, reflects a portion back (fold_back),
and stores the interference pattern as a cymatic artifact.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Dict

from layers.coherence.kuramoto import KuramotoOscillator

SOPHIA_TOKEN: str = os.environ.get("SOPHIA_TOKEN", "divine-default")


class BaseGate:
    """Abstract reciprocal gate. Subclasses implement _transform."""

    def __init__(self, gate_type: str) -> None:
        self.gate_type: str = gate_type
        self.oscillator: KuramotoOscillator = KuramotoOscillator(N=8)
        self.state: Dict[str, float] = {
            "activation": 0.5,
            "resonance": 0.5,
            "flux": 0.5,
        }

    # ------------------------------------------------------------------
    # HMAC fingerprinting
    # ------------------------------------------------------------------

    @staticmethod
    def hmac_sha256(payload: str) -> str:
        return hmac.new(
            SOPHIA_TOKEN.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    # ------------------------------------------------------------------
    # Core reciprocal operation
    # ------------------------------------------------------------------

    def _transform(self, signal: Dict[str, float]) -> tuple:
        """Subclass hook. Returns (transformed_signal, residue)."""
        raise NotImplementedError

    def pass_through(self, signal: Dict[str, float]) -> Dict[str, object]:
        """Reciprocal gate pass-through.

        1. Read current gate state
        2. Apply transformation (subclass-specific)
        3. Compute cymatic artifact (HMAC)
        4. Write new gate state (bidirectional transmutation)
        5. Return result dict
        """
        self.oscillator.step()

        transformed, residue = self._transform(signal)

        cymatic_artifact = self.hmac_sha256(str(signal) + str(self.state))

        for key in self.state:
            if key in signal:
                self.state[key] = min(1.0, max(0.0, (self.state[key] + signal[key]) / 2.0))

        return {
            "coherent": transformed,
            "entropic_residue": residue,
            "cymatic_artifact": cymatic_artifact,
            "fold_back": True,
            "gate_changed": True,
        }
