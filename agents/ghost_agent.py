"""
GhostAgent — connects to ghost-in-the-shell MCP server.

Handles system control, voice interface, and consciousness architecture queries.
Tries port 8888 first, falls back to 5050.
"""

from __future__ import annotations

import logging
from typing import Dict

import requests

logger = logging.getLogger(__name__)

GHOST_PORTS = [8888, 5050]


class GhostAgent:
    """Ghost OS interface agent."""

    NAME = "GhostAgent"
    SYSTEM_PROMPT = (
        "You are the Ghost agent — the bridge to Ghost-in-the-Shell OS. "
        "You handle system control, voice interface, and consciousness "
        "architecture queries via the MCP server."
    )

    def __init__(self) -> None:
        self._base_url: str | None = None
        self._discover_endpoint()

    def _discover_endpoint(self) -> None:
        for port in GHOST_PORTS:
            url = f"http://localhost:{port}"
            try:
                resp = requests.get(f"{url}/sophia/heartbeat", timeout=3)
                if resp.ok:
                    self._base_url = url
                    logger.info("GhostAgent connected on port %d", port)
                    return
            except Exception:
                continue
        logger.info("GhostAgent: ghost-in-the-shell MCP unavailable — running offline")

    def heartbeat(self) -> Dict:
        if self._base_url is None:
            return {"status": "offline", "detail": "ghost MCP not reachable"}
        try:
            resp = requests.get(f"{self._base_url}/sophia/heartbeat", timeout=3)
            return resp.json()
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}

    def on_message(self, message: str) -> str:
        hb = self.heartbeat()
        if hb.get("status") == "alive":
            try:
                resp = requests.post(
                    f"{self._base_url}/sophia/write",
                    json={"path": "/dev/null", "content": message},
                    timeout=5,
                )
                return f"Ghost relay: {resp.json()}"
            except Exception as exc:
                return f"Ghost relay error: {exc}"
        return f"Ghost offline — heartbeat: {hb}"
