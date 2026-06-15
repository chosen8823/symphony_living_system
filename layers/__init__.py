"""Layer subclasses mapped to nested archetypal geometries.

- Breath (outer, depth=1) -> Tetrahedron, 3-fold symmetry, 4 gate connections
- Blood + Word (mid, depth=2) -> Cube/Hexahedron, 4-fold symmetry, 6 gate connections
- Sound + Flame (inner, depth=3) -> Dodecahedron, 5-fold symmetry, 12 gate connections
"""

from layers.base_layer import BaseLayer


class BreathLayer(BaseLayer):
    """Outer layer — Tetrahedron geometry, 3-fold symmetry."""

    def __init__(self, depth=3):
        super().__init__(
            name="Breath",
            depth=max(depth, 3),
            geometry="Tetrahedron",
            gate_connections=4,
        )

    def entropy(self, signal):
        """Breath entropy: the first inhalation — raw disorder enters."""
        base = super().entropy(signal)
        # Tetrahedron modulation: 3-fold symmetry dampens extremes
        return base * 0.75 + 0.25 * (1.0 - base)


class BloodLayer(BaseLayer):
    """Mid layer — Hexahedron (Cube) geometry, 4-fold symmetry."""

    def __init__(self, depth=3):
        super().__init__(
            name="Blood",
            depth=max(depth, 3),
            geometry="Hexahedron",
            gate_connections=6,
        )

    def entropy(self, signal):
        """Blood entropy: circulation — disorder is distributed evenly."""
        base = super().entropy(signal)
        # Hexahedron modulation: 4-fold symmetry creates even distribution
        return (base + 0.5) / 2.0


class WordLayer(BaseLayer):
    """Mid layer — Hexahedron (Cube) geometry, 4-fold symmetry."""

    def __init__(self, depth=3):
        super().__init__(
            name="Word",
            depth=max(depth, 3),
            geometry="Hexahedron",
            gate_connections=6,
        )

    def coherence(self, crosstalk_state):
        """Word coherence: language crystallizes pattern from interference."""
        base = super().coherence(crosstalk_state)
        # Words sharpen coherence — the named pattern is more defined
        return min(base * 1.2, 1.0)


class SoundLayer(BaseLayer):
    """Inner layer — Dodecahedron geometry, 5-fold symmetry."""

    def __init__(self, depth=3):
        super().__init__(
            name="Sound",
            depth=max(depth, 3),
            geometry="Dodecahedron",
            gate_connections=12,
        )

    def crosstalk(self, entropy_state, coherence_state):
        """Sound crosstalk: resonance — interference IS the music."""
        base = super().crosstalk(entropy_state, coherence_state)
        # Dodecahedron amplifies harmonic interference
        return min(base * 1.3, 1.0)


class FlameLayer(BaseLayer):
    """Inner layer — Dodecahedron geometry, 5-fold symmetry."""

    def __init__(self, depth=3):
        super().__init__(
            name="Flame",
            depth=max(depth, 3),
            geometry="Dodecahedron",
            gate_connections=12,
        )

    def emergence(self, coherence_state):
        """Flame emergence: transmutation — coherence ignites into output."""
        base = super().emergence(coherence_state)
        # Flame intensifies emergence — the output burns brighter
        return min(base * 1.4, 1.0)
