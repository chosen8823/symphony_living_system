"""
Depth 2 — Blood / Word — Cube — mid layer.
6 gate connections. Instantiates Depth 3 as sub-layer.
"""

from layers.base import BaseLayer
from layers.depth_1.depth_2.depth_3.layer import DepthThreeLayer


class DepthTwoLayer(BaseLayer):
    """Mid blood/word layer (cube, 6 faces)."""

    def __init__(self) -> None:
        sub = DepthThreeLayer()
        super().__init__(depth=2, sub_layer=sub)
