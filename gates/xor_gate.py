"""
XOR Gate — the branching point gate.

Exclusive divergence: takes two input signals and returns the difference
signal (|a - b| for each field). The entropic_residue is the minimum of
the two signals (the discarded path), returned for fold_back.
"""

from typing import Dict, Tuple

from gates.base import BaseGate


class XORGate(BaseGate):
    """Branching point gate — exclusive divergence."""

    def __init__(self) -> None:
        super().__init__(gate_type="XOR")

    def _transform(self, signal: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """XOR transform: difference against internal gate state.

        For each field present in both signal and self.state,
        the coherent output is |signal - state| (the divergence)
        and the residue is min(signal, state) (the discarded path).
        """
        transformed: Dict[str, float] = {}
        residue: Dict[str, float] = {}
        for key, value in signal.items():
            if isinstance(value, (int, float)):
                clamped = min(1.0, max(0.0, float(value)))
                gate_val = self.state.get(key, 0.5)
                transformed[key] = abs(clamped - gate_val)
                residue[key] = min(clamped, gate_val)
            else:
                transformed[key] = value
                residue[key] = value
        return transformed, residue
