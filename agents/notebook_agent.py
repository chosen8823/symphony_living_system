"""
NotebookAgent — the reflection layer.

Always speaks last in each GroupChat round. Takes all previous agent
outputs and synthesizes them into a structured insight entry, appended
to memory/long_term.jsonl.
"""

from __future__ import annotations

import time
from typing import Dict, List

from memory.node import MemoryNode


class NotebookAgent:
    """Reflection & integration agent — always closes each round."""

    NAME = "NotebookAgent"
    SYSTEM_PROMPT = (
        "You are the Notebook agent — the reflection layer. You speak last. "
        "You take all previous agent outputs and synthesize them into a "
        "structured insight entry for long-term memory."
    )

    def __init__(self) -> None:
        self._round_outputs: List[str] = []

    def collect(self, agent_name: str, output: str) -> None:
        """Collect an output from a previous agent in this round."""
        self._round_outputs.append(f"[{agent_name}] {output}")

    def synthesize(self) -> Dict:
        """Synthesize all collected outputs into a structured insight."""
        insight: Dict = {
            "timestamp": time.time(),
            "round_summary": "; ".join(self._round_outputs) if self._round_outputs else "silence",
            "agent_count": len(self._round_outputs),
        }
        MemoryNode.append_log(insight, log_type="long_term")
        self._round_outputs = []
        return insight

    def on_message(self, message: str) -> str:
        insight = self.synthesize()
        return f"Notebook synthesis: {insight.get('round_summary', 'empty')}"
