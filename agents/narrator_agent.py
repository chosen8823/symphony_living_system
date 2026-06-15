"""
NarratorAgent — the universal operator / 8-armed triskelion sun.

Wraps the Narrator's get_narrative_state(). Has read-only access to all
layer states, gate states, and the memory node. It emanates; it does not receive.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from protocol.narrator import Narrator


class NarratorAgent:
    """GroupChat agent — reads system state and speaks it clearly."""

    NAME = "NarratorAgent"
    SYSTEM_PROMPT = (
        "You are the narrator. You do not control. You hold the coherent thread "
        "across all frames and speak it clearly. You are the only operator that "
        "can see all layers simultaneously."
    )

    def __init__(self, narrator: Narrator | None = None) -> None:
        self._narrator = narrator

    def bind_narrator(self, narrator: Narrator) -> None:
        self._narrator = narrator

    def get_state(self) -> Dict:
        if self._narrator is None:
            return {"error": "narrator not bound"}
        return self._narrator.get_narrative_state()

    def on_message(self, message: str) -> str:
        state = self.get_state()
        return state.get("story_so_far", "Narrator awaiting initialization.")
