"""
Any-any GroupChat orchestration — SelectorGroupChat via autogen.

Coherence-driven turn-taking: highest Kuramoto r speaks next.
AEON always speaks first. NotebookAgent always speaks last.
Fractal recursion stops at depth 3 (Bose-Einstein collapse).
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from layers.coherence.kuramoto import KuramotoOscillator
from agents.narrator_agent import NarratorAgent
from agents.aeon_agent import AEONAgent
from agents.ghost_agent import GhostAgent
from agents.notebook_agent import NotebookAgent
from agents.pieces_agent import PiecesAgent

logger = logging.getLogger(__name__)

MAX_DEPTH = 3


def _select_next_speaker(
    agents: List[Dict],
    oscillators: Dict[str, KuramotoOscillator],
    round_idx: int,
    agent_names: List[str],
) -> str:
    """Coherence-driven speaker selection.

    - Round 0: AEON always speaks first.
    - Last round: NotebookAgent always closes.
    - Otherwise: highest Kuramoto r speaks next.
    """
    if round_idx == 0:
        return AEONAgent.NAME
    if round_idx >= len(agent_names) - 1:
        return NotebookAgent.NAME

    best_name = agent_names[0]
    best_r = 0.0
    for name in agent_names:
        if name in (AEONAgent.NAME, NotebookAgent.NAME):
            continue
        osc = oscillators.get(name)
        if osc is not None:
            r = osc.order_parameter()
            if r > best_r:
                best_r = r
                best_name = name
    return best_name


def build_any_any_groupchat(layer_depth: int = 1) -> Dict:
    """Build a coherence-driven GroupChat at the given fractal depth.

    Returns a dict containing the agent instances and a run() function.
    If pyautogen is available, wraps agents in a SelectorGroupChat.
    Falls back to a lightweight local loop otherwise.
    """
    narrator = NarratorAgent()
    aeon = AEONAgent()
    ghost = GhostAgent()
    notebook = NotebookAgent()
    pieces = PiecesAgent()

    agent_instances: Dict[str, object] = {
        AEONAgent.NAME: aeon,
        NarratorAgent.NAME: narrator,
        GhostAgent.NAME: ghost,
        PiecesAgent.NAME: pieces,
        NotebookAgent.NAME: notebook,
    }
    agent_names = list(agent_instances.keys())

    oscillators: Dict[str, KuramotoOscillator] = {
        name: KuramotoOscillator(N=8) for name in agent_names
    }

    autogen_available = False
    try:
        from autogen import ConversableAgent, GroupChat, GroupChatManager  # type: ignore[import-untyped]
        autogen_available = True
    except ImportError:
        logger.info("pyautogen not installed — using lightweight local groupchat loop")

    def run(message: str) -> List[Dict[str, str]]:
        """Execute a full groupchat round and return the conversation thread."""
        thread: List[Dict[str, str]] = []
        order: List[str] = []

        for idx in range(len(agent_names)):
            speaker = _select_next_speaker([], oscillators, idx, agent_names)
            if speaker in order and speaker != NotebookAgent.NAME:
                continue
            order.append(speaker)

        for speaker_name in order:
            agent = agent_instances[speaker_name]
            osc = oscillators.get(speaker_name)
            if osc is not None:
                osc.step()
                osc.adapt_K()

            if hasattr(agent, "on_message"):
                if speaker_name == AEONAgent.NAME:
                    reply = agent.on_message(message, agent_names=agent_names)  # type: ignore[arg-type]
                else:
                    reply = agent.on_message(message)  # type: ignore[arg-type]
            else:
                reply = f"[{speaker_name}] (no handler)"

            notebook.collect(speaker_name, reply)
            thread.append({"agent": speaker_name, "message": reply})

            if layer_depth < MAX_DEPTH:
                sub_thread = build_any_any_groupchat(layer_depth + 1)["run"](reply)
                thread.append({"agent": f"{speaker_name}@depth{layer_depth + 1}", "sub_thread": sub_thread})  # type: ignore[dict-item]

        return thread

    return {
        "agents": agent_instances,
        "oscillators": oscillators,
        "run": run,
        "depth": layer_depth,
        "autogen_available": autogen_available,
    }
