"""
MemoryNode — locked persistent storage requiring resonance to unlock.

Append-only memory: short_term.jsonl and long_term.jsonl are never overwritten.
Cymatic artifacts are stored as individual JSON files under memory/artifacts/.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, List

_MEMORY_DIR = Path(__file__).resolve().parent


class MemoryNodeLocked(Exception):
    """Raised when a write is attempted on a locked memory node."""


class MemoryNode:
    """Floating sphere — a persistent memory node gated by Kuramoto coherence."""

    def __init__(self, unlock_condition: float = 0.8) -> None:
        self.locked: bool = True
        self.artifacts: List[Dict] = []
        self.unlock_condition: float = unlock_condition

    # ------------------------------------------------------------------
    # Unlock
    # ------------------------------------------------------------------

    def try_unlock(self, r: float, cymatic_artifact: str) -> bool:
        """Unlock if Kuramoto r >= threshold AND artifact is a valid HMAC string."""
        if r >= self.unlock_condition and isinstance(cymatic_artifact, str) and cymatic_artifact:
            self.locked = False
            return True
        return False

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    def store(self, artifact: Dict) -> None:
        """Store a cymatic artifact. Raises MemoryNodeLocked if still locked."""
        if self.locked:
            raise MemoryNodeLocked("Memory node is locked — coherence threshold not met.")
        self.artifacts.append(artifact)
        artifact_dir = _MEMORY_DIR / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        ts = str(int(time.time() * 1000))
        artifact_path = artifact_dir / f"{ts}.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)

    @staticmethod
    def append_log(entry: Dict, log_type: str = "short_term") -> None:
        """Append a JSON entry to the appropriate .jsonl log. Always append, never overwrite."""
        filename = "short_term.jsonl" if log_type == "short_term" else "long_term.jsonl"
        log_path = _MEMORY_DIR / filename
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
