"""
AEONAgent — self-configuring orchestrator.

Connects to chosen8823/AEON via HTTP if available.
On first message, maps all connected agents and their states.
Falls back to reading memory/ directory if AEON is unavailable.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

_MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"
AEON_URL = "http://localhost:5050"


class AEONAgent:
    """Self-discovery / mapping agent — always speaks first in a new session."""

    NAME = "AEONAgent"
    SYSTEM_PROMPT = (
        "You are AEON, the self-configuring orchestrator. On activation you map "
        "every connected agent and its current state, then report the topology."
    )

    def __init__(self) -> None:
        self._mapped: bool = False
        self._agent_map: List[Dict] = []

    def _try_aeon_http(self) -> Dict | None:
        try:
            resp = requests.get(f"{AEON_URL}/sophia/heartbeat", timeout=3)
            if resp.ok:
                return resp.json()
        except Exception:
            logger.debug("AEON HTTP unavailable — falling back to memory directory")
        return None

    def _read_memory_fallback(self) -> List[Dict]:
        entries: List[Dict] = []
        log_path = _MEMORY_DIR / "short_term.jsonl"
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return entries

    def map_agents(self, agent_names: List[str]) -> List[Dict]:
        """Map all connected agents. Called on first message."""
        aeon_status = self._try_aeon_http()
        self._agent_map = [
            {"name": name, "aeon_connected": aeon_status is not None}
            for name in agent_names
        ]
        if aeon_status is None:
            fallback = self._read_memory_fallback()
            self._agent_map.append({"memory_entries": len(fallback)})
        self._mapped = True
        return self._agent_map

    def on_message(self, message: str, agent_names: List[str] | None = None) -> str:
        if not self._mapped and agent_names:
            self.map_agents(agent_names)
        topology = json.dumps(self._agent_map, indent=2) if self._agent_map else "[]"
        return f"AEON topology map: {topology}"
