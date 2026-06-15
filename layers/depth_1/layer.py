"""
Depth 1 — Breath — Tetrahedron — outer layer.
4 gate connections. Instantiates Depth 2 as sub-layer.
"""

from layers.base import BaseLayer
from layers.depth_1.depth_2.layer import DepthTwoLayer


class DepthOneLayer(BaseLayer):
    """Outer breath layer (tetrahedron, 4 faces)."""

    def __init__(self) -> None:
        sub = DepthTwoLayer()
        super().__init__(depth=1, sub_layer=sub)
