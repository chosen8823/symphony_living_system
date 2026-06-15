"""
BaseLayer — fractal toroidal layer with 4-phase cycle.

Phase cycle per temporal frame:
  1. entropy(t)   — Shannon entropy of the incoming signal
  2. crosstalk(t) — entropy * coherence (interference product)
  3. coherence(t) — Kuramoto order parameter r
  4. emergence(t) — (coherence - entropy) * crosstalk

Toroidal fold: emergence(t) -> entropy(t+1)
"""

from __future__ import annotations

import math
from typing import Dict, Optional

from layers.coherence.kuramoto import KuramotoOscillator


class BaseLayer:
    """Recursive fractal layer. Recursion stops at depth 3 (Bose-Einstein collapse)."""

    GEOMETRY_MAP = {
        1: ("tetrahedron", 4),
        2: ("cube", 6),
        3: ("dodecahedron", 12),
    }

    def __init__(self, depth: int = 1, sub_layer: Optional[BaseLayer] = None) -> None:
        if depth not in self.GEOMETRY_MAP:
            raise ValueError(f"depth must be 1, 2, or 3; got {depth}")
        self.depth: int = depth
        self.geometry: str = self.GEOMETRY_MAP[depth][0]
        self.gate_connections: int = self.GEOMETRY_MAP[depth][1]
        self.oscillator: KuramotoOscillator = KuramotoOscillator(N=8)
        self.sub_layer: Optional[BaseLayer] = sub_layer
        self._last_emergence: float = 0.0

    # ------------------------------------------------------------------
    # 4-phase cycle
    # ------------------------------------------------------------------

    @staticmethod
    def _shannon_entropy(signal: Dict[str, float]) -> float:
        """Shannon entropy of the value distribution (gradient floats 0-1)."""
        values = [v for v in signal.values() if isinstance(v, (int, float))]
        if not values:
            return 0.0
        total = sum(values) or 1e-12
        probs = [v / total for v in values]
        return -sum(p * math.log2(p) if p > 0 else 0.0 for p in probs)

    def _entropy(self, signal: Dict[str, float]) -> float:
        raw = self._shannon_entropy(signal)
        max_ent = math.log2(max(len(signal), 2))
        return min(1.0, raw / max_ent) if max_ent > 0 else 0.0

    def _coherence(self) -> float:
        return self.oscillator.order_parameter()

    def _crosstalk(self, entropy: float, coherence: float) -> float:
        return entropy * coherence

    @staticmethod
    def _emergence(coherence: float, entropy: float, crosstalk: float) -> float:
        return (coherence - entropy) * crosstalk

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def phase_cycle(self, signal: Dict[str, float]) -> Dict[str, float]:
        """Run the full 4-phase cycle on *signal*. Returns the emergence dict."""
        self.oscillator.step()
        self.oscillator.adapt_K()

        ent = self._entropy(signal)
        coh = self._coherence()
        xtk = self._crosstalk(ent, coh)
        emg = self._emergence(coh, ent, xtk)

        self._last_emergence = emg

        result: Dict[str, float] = {
            "entropy": ent,
            "coherence": coh,
            "crosstalk": xtk,
            "emergence": emg,
            "depth": float(self.depth),
            "kuramoto_r": coh,
            "K": self.oscillator.K,
        }

        if self.sub_layer is not None:
            sub_result = self.sub_layer.phase_cycle(result)
            result["sub_layer"] = sub_result  # type: ignore[assignment]

        return result

    def fold_back(self, emergence: Dict[str, float]) -> Dict[str, float]:
        """Toroidal fold: emergence(t) becomes entropy(t+1).

        Returns the fold-back signal ready for the next phase_cycle call.
        """
        fold_signal = dict(emergence)
        fold_signal["fold_back_active"] = 1.0
        fold_signal["entropy_seed"] = emergence.get("emergence", 0.0)
        return fold_signal
