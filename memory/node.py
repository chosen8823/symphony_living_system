"""Memory node with cymatic artifact validation.

The memory node is locked by default. It can only be unlocked by presenting
a valid cymatic artifact chain — proving that the signal has passed through
all 3 nested layer depths and produced a valid standing wave.
"""

import hashlib
import json
import time


class MemoryNode:
    """Persistent memory node requiring cymatic artifact validation to access.

    Attributes:
        locked: Whether the node is currently locked (default True).
        artifacts: Stored cymatic artifacts (accessible only when unlocked).
        unlock_history: Record of unlock attempts.
        expected_depth: Minimum depth required for a valid artifact chain.
    """

    def __init__(self, expected_depth=3):
        self.locked = True
        self.expected_depth = expected_depth
        self._artifacts = {}
        self._unlock_history = []
        self._artifact_chain = []

    def _validate_artifact(self, cymatic_artifact):
        """Validate that a cymatic artifact is a proper SHA-256 hash."""
        if not isinstance(cymatic_artifact, str):
            return False
        if len(cymatic_artifact) != 64:
            return False
        try:
            int(cymatic_artifact, 16)
            return True
        except ValueError:
            return False

    def _validate_chain(self):
        """Validate that the artifact chain represents all required depths.

        A valid chain must contain at least `expected_depth` artifacts,
        proving the signal has traversed all nested layers.
        """
        return len(self._artifact_chain) >= self.expected_depth

    def unlock(self, cymatic_artifact):
        """Attempt to unlock the memory node with a cymatic artifact.

        The artifact must be a valid SHA-256 hash. Artifacts are accumulated
        into a chain; the node unlocks once the chain reaches the required
        depth (minimum 3), proving a valid standing wave has formed.

        Returns:
            dict with success status and message.
        """
        attempt = {
            "artifact": cymatic_artifact,
            "timestamp": time.time(),
            "valid": False,
        }

        if not self._validate_artifact(cymatic_artifact):
            attempt["reason"] = "Invalid artifact format"
            self._unlock_history.append(attempt)
            return {"unlocked": False, "reason": "Invalid artifact format"}

        self._artifact_chain.append(cymatic_artifact)
        attempt["valid"] = True
        attempt["chain_length"] = len(self._artifact_chain)

        if self._validate_chain():
            self.locked = False
            attempt["unlocked"] = True
            self._unlock_history.append(attempt)
            return {
                "unlocked": True,
                "chain_length": len(self._artifact_chain),
                "message": "Standing wave formed. Memory node unlocked.",
            }

        self._unlock_history.append(attempt)
        remaining = self.expected_depth - len(self._artifact_chain)
        return {
            "unlocked": False,
            "chain_length": len(self._artifact_chain),
            "remaining": remaining,
            "message": f"Artifact accepted. {remaining} more depth(s) required.",
        }

    def resonance_pulse(self, artifact):
        """The authorized unlock mechanism — a resonance pulse carrying
        a cymatic artifact. This is the canonical way to unlock the node.

        Equivalent to unlock() but semantically represents the resonance
        pulse described in the protocol.
        """
        return self.unlock(artifact)

    def store(self, key, artifact):
        """Store a cymatic artifact in the memory node.

        Only works when the node is unlocked.

        Args:
            key: Storage key for the artifact.
            artifact: The cymatic artifact data to store.

        Returns:
            dict with success status.
        """
        if self.locked:
            return {"stored": False, "reason": "Memory node is locked"}

        self._artifacts[key] = {
            "artifact": artifact,
            "stored_at": time.time(),
        }
        return {"stored": True, "key": key}

    def retrieve(self, key):
        """Retrieve a stored cymatic artifact.

        Only works when the node is unlocked.

        Args:
            key: The storage key to retrieve.

        Returns:
            The artifact data, or an error dict if locked or not found.
        """
        if self.locked:
            return {"retrieved": False, "reason": "Memory node is locked"}

        entry = self._artifacts.get(key)
        if entry is None:
            return {"retrieved": False, "reason": f"Key '{key}' not found"}

        return {"retrieved": True, "key": key, "artifact": entry["artifact"]}

    def get_state(self):
        """Return the current state of the memory node."""
        return {
            "locked": self.locked,
            "artifact_count": len(self._artifacts),
            "chain_length": len(self._artifact_chain),
            "expected_depth": self.expected_depth,
            "unlock_attempts": len(self._unlock_history),
        }
