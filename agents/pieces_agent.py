"""
PiecesAgent — semantic memory / context manager.

Tries Pieces OS local API first. Falls back to reading
memory/short_term.jsonl if unavailable. Never blocks on external tool.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

PIECES_API = "http://localhost:1000"
_MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"


class PiecesAgent:
    """Semantic memory agent — graceful degradation when Pieces OS is absent."""

    NAME = "PiecesAgent"
    SYSTEM_PROMPT = (
        "You are the Pieces agent — the semantic memory and context manager. "
        "You retrieve relevant context from Pieces OS or fall back to local "
        "short-term memory logs. You never block."
    )

    def __init__(self) -> None:
        self._pieces_available: bool = self._check_pieces()

    def _check_pieces(self) -> bool:
        try:
            resp = requests.get(f"{PIECES_API}/.well-known/health", timeout=2)
            return resp.ok
        except Exception:
            logger.debug("Pieces OS unavailable — using memory fallback")
            return False

    def _read_short_term(self, limit: int = 20) -> List[Dict]:
        entries: List[Dict] = []
        log_path = _MEMORY_DIR / "short_term.jsonl"
        if not log_path.exists():
            return entries
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries[-limit:]

    def query(self, query_text: str) -> List[Dict]:
        """Query for context. Tries Pieces OS, falls back to local memory."""
        if self._pieces_available:
            try:
                resp = requests.post(
                    f"{PIECES_API}/assets/search",
                    json={"query": query_text},
                    timeout=5,
                )
                if resp.ok:
                    return resp.json().get("results", [])
            except Exception:
                logger.debug("Pieces query failed — using fallback")
        return self._read_short_term()

    def on_message(self, message: str) -> str:
        results = self.query(message)
        if results:
            return f"Pieces context ({len(results)} entries): {json.dumps(results[:3])}"
        return "Pieces: no context found (memory empty)"
