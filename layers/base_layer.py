"""Base layer for the toroidal fractal grating engine.

Each layer runs a 4-phase cycle: entropy -> crosstalk -> coherence -> emergence.
Layers are self-similar (fractal) and support nested sub-layers via a depth parameter.
"""

import hashlib
import json
import time


class BaseLayer:
    """Base class for all layers in the symphony living system.

    Attributes:
        name: Human-readable name for this layer.
        depth: Fractal nesting depth (minimum viable = 3).
        geometry: The archetypal geometry constraining gate connections.
        gate_connections: Number of valid gate connections at this depth.
        sub_layers: Nested sub-layers for fractal self-similarity.
        state: Current internal state of the layer.
    """

    GEOMETRY_MAP = {
        1: ("Tetrahedron", 4),
        2: ("Hexahedron", 6),
        3: ("Dodecahedron", 12),
    }

    def __init__(self, name, depth=3, geometry=None, gate_connections=None, _is_sub=False):
        self.name = name
        self.depth = depth if _is_sub else max(depth, 3)
        if geometry and gate_connections is not None:
            self.geometry = geometry
            self.gate_connections = gate_connections
        else:
            geo_name, geo_connections = self.GEOMETRY_MAP.get(
                min(depth, 3), ("Dodecahedron", 12)
            )
            self.geometry = geo_name
            self.gate_connections = geo_connections

        self.sub_layers = []
        self.state = {
            "entropy_level": 0.0,
            "coherence_level": 0.0,
            "crosstalk_level": 0.0,
            "emergence_level": 0.0,
            "last_signal": None,
            "frame": 0,
        }
        self._init_sub_layers()

    def _init_sub_layers(self):
        """Initialize fractal sub-layers up to the configured depth."""
        if self.depth > 1:
            child_depth = self.depth - 1
            geo_name, geo_connections = self.GEOMETRY_MAP.get(
                min(child_depth, 3), ("Dodecahedron", 12)
            )
            sub = BaseLayer(
                name=f"{self.name}_sub_{child_depth}",
                depth=child_depth,
                geometry=geo_name,
                gate_connections=geo_connections,
                _is_sub=True,
            )
            self.sub_layers.append(sub)

    def entropy(self, signal):
        """Phase 1: Measure disorder in the incoming signal.

        Returns a float representing the entropy level (0.0 = pure order,
        1.0 = maximum disorder).
        """
        if signal is None:
            self.state["entropy_level"] = 1.0
            return 1.0

        signal_str = json.dumps(signal, sort_keys=True, default=str)
        byte_values = list(signal_str.encode("utf-8"))
        if not byte_values:
            self.state["entropy_level"] = 1.0
            return 1.0

        mean = sum(byte_values) / len(byte_values)
        variance = sum((b - mean) ** 2 for b in byte_values) / len(byte_values)
        normalized = min(variance / 6400.0, 1.0)
        self.state["entropy_level"] = normalized
        return normalized

    def crosstalk(self, entropy_state, coherence_state):
        """Phase 2: Compute interference between entropy and coherence.

        Crosstalk IS the signal — it represents the productive interference
        pattern between order and disorder.
        """
        interference = abs(entropy_state - coherence_state)
        product = entropy_state * coherence_state
        crosstalk_value = (interference + product) / 2.0
        self.state["crosstalk_level"] = crosstalk_value
        return crosstalk_value

    def coherence(self, crosstalk_state):
        """Phase 3: Extract the ordered pattern from the crosstalk.

        Returns a float representing the coherence level (0.0 = no pattern,
        1.0 = perfect coherence).
        """
        coherence_value = 1.0 - crosstalk_state if crosstalk_state < 1.0 else 0.0
        self.state["coherence_level"] = coherence_value
        return coherence_value

    def emergence(self, coherence_state):
        """Phase 4: Produce the output from the coherent pattern.

        Returns the emergent output — the signal that will become
        entropy(t+1) in the toroidal fold.
        """
        emergence_value = coherence_state * (1.0 + self.state["entropy_level"]) / 2.0
        self.state["emergence_level"] = emergence_value
        return emergence_value

    def _compute_cymatic_artifact(self, entropy_val, crosstalk_val, coherence_val, emergence_val):
        """Compute the SHA-256 hash of the interference pattern across all 4 phases."""
        pattern = json.dumps({
            "entropy": entropy_val,
            "crosstalk": crosstalk_val,
            "coherence": coherence_val,
            "emergence": emergence_val,
            "layer": self.name,
            "depth": self.depth,
            "frame": self.state["frame"],
            "timestamp": time.time(),
        }, sort_keys=True)
        return hashlib.sha256(pattern.encode("utf-8")).hexdigest()

    def process(self, signal):
        """Run the full 4-phase cycle and return the result.

        The toroidal structure means fold_back=True: the entropic_residue
        should re-enter the system at the previous layer.
        """
        self.state["last_signal"] = signal
        self.state["frame"] += 1

        entropy_val = self.entropy(signal)
        previous_coherence = self.state.get("coherence_level", 0.5)
        crosstalk_val = self.crosstalk(entropy_val, previous_coherence)
        coherence_val = self.coherence(crosstalk_val)
        emergence_val = self.emergence(coherence_val)

        # Process through sub-layers (fractal recursion)
        sub_artifacts = []
        for sub_layer in self.sub_layers:
            sub_result = sub_layer.process(signal)
            sub_artifacts.append(sub_result["cymatic_artifact"])

        cymatic_artifact = self._compute_cymatic_artifact(
            entropy_val, crosstalk_val, coherence_val, emergence_val
        )

        # Chain sub-artifacts into the main artifact
        if sub_artifacts:
            chain = cymatic_artifact + "".join(sub_artifacts)
            cymatic_artifact = hashlib.sha256(chain.encode("utf-8")).hexdigest()

        return {
            "coherent_output": emergence_val,
            "entropic_residue": entropy_val,
            "cymatic_artifact": cymatic_artifact,
            "fold_back": True,
            "layer": self.name,
            "depth": self.depth,
            "frame": self.state["frame"],
            "sub_artifacts": sub_artifacts,
        }

    def get_state(self):
        """Return the current state of this layer and all sub-layers."""
        state = dict(self.state)
        state["name"] = self.name
        state["depth"] = self.depth
        state["geometry"] = self.geometry
        state["gate_connections"] = self.gate_connections
        state["sub_layers"] = [sl.get_state() for sl in self.sub_layers]
        return state
