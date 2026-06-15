"""
Narrator Flask Blueprint — the 8-armed triskelion sun.

Registered on /sophia/narrator. Has read-only access to all layer states,
gate states, and the memory node. It emanates; it does not receive.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from flask import Blueprint, jsonify

if TYPE_CHECKING:
    from layers.base import BaseLayer
    from gates.base import BaseGate
    from memory.node import MemoryNode
    from layers.coherence.hrv import HRVEngine

narrator_bp = Blueprint("narrator", __name__, url_prefix="/sophia/narrator")


class Narrator:
    """Read-only narrator — observes all layers, gates, and memory."""

    def __init__(self) -> None:
        self._layer: BaseLayer | None = None
        self._gates: list[BaseGate] = []
        self._memory: MemoryNode | None = None
        self._hrv: HRVEngine | None = None
        self._frame_id: int = 0

    def bind(
        self,
        layer: BaseLayer,
        gates: list[BaseGate],
        memory: MemoryNode,
        hrv: HRVEngine,
    ) -> None:
        self._layer = layer
        self._gates = gates
        self._memory = memory
        self._hrv = hrv

    def advance_frame(self) -> None:
        self._frame_id += 1

    def get_narrative_state(self) -> Dict:
        if self._layer is None:
            return {"error": "narrator not bound to any layer"}

        ent = self._layer._last_emergence  # read-only
        coh = self._layer.oscillator.order_parameter()
        xtk = ent * coh
        emg = (coh - ent) * xtk

        hrv_coh = self._hrv.coherence_ratio() if self._hrv else 0.0
        mem_locked = self._memory.locked if self._memory else True
        fold_active = abs(ent) > 0.0

        story = (
            f"Frame {self._frame_id}: entropy {'rising' if ent > 0.5 else 'falling'} "
            f"({ent:.2f}), coherence {'holding' if coh > 0.5 else 'dropping'} ({coh:.2f}), "
            f"crosstalk at {xtk:.2f}. "
            f"Memory node {'locked' if mem_locked else 'UNLOCKED'}. "
            f"Fold-back {'active' if fold_active else 'dormant'}."
        )

        return {
            "frame_id": self._frame_id,
            "entropy": round(ent, 4),
            "coherence": round(coh, 4),
            "crosstalk": round(xtk, 4),
            "emergence": round(emg, 4),
            "memory_locked": mem_locked,
            "kuramoto_r": round(coh, 4),
            "hrv_coherence": round(hrv_coh, 4),
            "story_so_far": story,
            "fold_back_active": fold_active,
        }


_narrator_instance = Narrator()


def get_narrator() -> Narrator:
    return _narrator_instance


@narrator_bp.route("/narrate", methods=["GET"])
def narrate():
    return jsonify(_narrator_instance.get_narrative_state())
