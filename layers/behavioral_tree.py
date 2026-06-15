import os
import json
import hmac
import hashlib
import threading
import time
from datetime import datetime
from typing import Callable


MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory")
BT_LOG_PATH = os.path.join(MEMORY_DIR, "bt_log.jsonl")


class BTNode:
    """Base behavioral-tree node. tick() returns float 0.0-1.0 (never boolean)."""

    def __init__(self, name: str):
        self.name = name
        self.children: list["BTNode"] = []
        self.parent: "BTNode | None" = None

    def tick(self) -> float:
        raise NotImplementedError

    def add_child(self, child: "BTNode"):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "BTNode"):
        self.children.remove(child)
        child.parent = None


class SequenceNode(BTNode):
    """Fails (< 0.5) if any child < 0.5. Returns average of children."""

    def tick(self) -> float:
        if not self.children:
            return 0.0
        total = 0.0
        for child in self.children:
            val = child.tick()
            if val < 0.5:
                return val
            total += val
        return total / len(self.children)


class SelectorNode(BTNode):
    """Succeeds (>= 0.5) if any child >= 0.5. Returns max of children."""

    def tick(self) -> float:
        if not self.children:
            return 0.0
        best = 0.0
        for child in self.children:
            val = child.tick()
            if val >= 0.5:
                return val
            best = max(best, val)
        return best


class ParallelNode(BTNode):
    """Runs all children. Returns average."""

    def tick(self) -> float:
        if not self.children:
            return 0.0
        vals = [c.tick() for c in self.children]
        return sum(vals) / len(vals)


class LeafNode(BTNode):
    """Leaf node wrapping a callable that returns float 0.0-1.0."""

    def __init__(self, name: str, action: Callable[[], float]):
        super().__init__(name)
        self._action = action

    def tick(self) -> float:
        try:
            val = self._action()
            if isinstance(val, (int, float)):
                return max(0.0, min(1.0, float(val)))
            return 0.5
        except Exception:
            return 0.0


class AdaptiveScriptEngine:
    """Monitors coherence and restructures the behavioral tree.

    If r < 0.3 (high entropy): prunes lowest-coherence branch and promotes its sibling.
    If r > 0.8: adds a new Leaf node to the highest-coherence branch.
    Self-similar restructuring only -- never creates new node types.
    """

    def __init__(self, root: BTNode, kuramoto, layers, gates, narrator):
        self.root = root
        self.kuramoto = kuramoto
        self.layers = layers
        self.gates = gates
        self.narrator = narrator
        self._running = False
        self._thread = None

    def tick_once(self) -> dict:
        """Tick the tree once and return state."""
        result = self.root.tick()
        r = self.kuramoto.order_parameter()

        if r < 0.3:
            self._restructure_prune()
        elif r > 0.8:
            self._restructure_grow()

        entry = {
            "ts": datetime.utcnow().isoformat(),
            "tree_result": result,
            "kuramoto_r": r,
            "tree_name": self.root.name,
        }

        self._log(entry)
        return entry

    def start_monitor(self, interval: float = 5.0):
        """Start background monitoring thread (every `interval` seconds)."""
        if self._running:
            return
        self._running = True

        def _loop():
            while self._running:
                self.tick_once()
                time.sleep(interval)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop_monitor(self):
        self._running = False

    def _restructure_prune(self):
        """Prune lowest-coherence branch and promote its sibling."""
        candidates = self._collect_leaves(self.root)
        if len(candidates) < 2:
            return
        candidates.sort(key=lambda leaf: leaf.tick())
        weakest = candidates[0]
        parent = weakest.parent
        if parent and len(parent.children) > 1:
            parent.remove_child(weakest)

    def _restructure_grow(self):
        """Add a Leaf clone to the highest-coherence branch."""
        candidates = self._collect_leaves(self.root)
        if not candidates:
            return
        candidates.sort(key=lambda leaf: leaf.tick(), reverse=True)
        strongest = candidates[0]
        parent = strongest.parent
        if parent is None:
            return
        new_leaf = LeafNode(
            name=f"{strongest.name}_clone_{len(parent.children)}",
            action=strongest._action,
        )
        parent.add_child(new_leaf)

    def _collect_leaves(self, node: BTNode) -> list[LeafNode]:
        if isinstance(node, LeafNode):
            return [node]
        result = []
        for child in node.children:
            result.extend(self._collect_leaves(child))
        return result

    def _log(self, entry: dict):
        os.makedirs(os.path.dirname(BT_LOG_PATH), exist_ok=True)
        token = os.environ.get("SOPHIA_TOKEN", "divine-default")
        payload = json.dumps(entry, sort_keys=True)
        fingerprint = hmac.new(
            token.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()[:16]
        entry["hmac"] = fingerprint
        with open(BT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")


def build_seed_tree(layers: dict, gates: dict, kuramoto, narrator) -> BTNode:
    """Build the minimum 3-depth seed tree per spec."""
    root = SequenceNode("root")

    observe = SelectorNode("observe")
    observe.add_child(
        LeafNode("breath_check", action=lambda: layers["breath"].state["coherence"])
    )
    observe.add_child(
        LeafNode("gate_check", action=lambda: gates["nor_d1_0"].state)
    )
    root.add_child(observe)

    act = SequenceNode("act")
    act.add_child(
        LeafNode(
            "tick_layers",
            action=lambda: max(
                0.0,
                min(
                    1.0,
                    sum(l.tick({}).get("coherent", {}).get("value", 0.5) for l in layers.values())
                    / max(len(layers), 1),
                ),
            ),
        )
    )
    act.add_child(
        LeafNode("step_kuramoto", action=lambda: min(1.0, kuramoto.step()))
    )
    root.add_child(act)

    root.add_child(
        LeafNode(
            "narrate",
            action=lambda: 1.0 if narrator.observe().get("status") == "ready_for_coalesce" else 0.5,
        )
    )

    return root
