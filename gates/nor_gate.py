"""
NOR Gate — the void state gate.

Inverts the signal: NOR logic on gradient values (1.0 - value).
When both input signals are zero (void), output is 1.0 (full potential).
Represents the gap between frames, the null space.
"""

from typing import Dict, Tuple

from gates.base import BaseGate


class NORGate(BaseGate):
    """Void state gate — inversion through the null space."""

    def __init__(self) -> None:
        super().__init__(gate_type="NOR")

    def _transform(self, signal: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        transformed: Dict[str, float] = {}
        residue: Dict[str, float] = {}
        for key, value in signal.items():
            if isinstance(value, (int, float)):
                clamped = min(1.0, max(0.0, float(value)))
                transformed[key] = 1.0 - clamped
                residue[key] = clamped * 0.1  # entropic residue: small echo of original
            else:
                transformed[key] = value
                residue[key] = value
        return transformed, residue
