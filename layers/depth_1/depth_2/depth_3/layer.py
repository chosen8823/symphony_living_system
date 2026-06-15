"""
Depth 3 — Sound / Flame — Dodecahedron — inner layer.
12 gate connections. No sub-layer (Bose-Einstein collapse point).
"""

from layers.base import BaseLayer


class DepthThreeLayer(BaseLayer):
    """Inner sound/flame layer (dodecahedron, 12 faces). Terminal depth."""

    def __init__(self) -> None:
        super().__init__(depth=3, sub_layer=None)
