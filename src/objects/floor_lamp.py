from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Cylinder

@dataclass
class FloorLamp(Group):
    height: float = 1.6
    base_color: Color = field(default_factory=lambda: COLORS["DARK_GRAY"])
    shade_color: Color = field(default_factory=lambda: Color(0.98, 0.85, 0.5, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        base_h = 0.03
        shade_h = 0.22
        pole_h = self.height - base_h - shade_h
        if pole_h <= 0:
            raise ValueError("FloorLamp is too short")

        self.parts = [
            Cylinder(
                radius=0.12,
                height=base_h,
                segments=8,
                transform=Transform.at(0, base_h / 2, 0),
                color=self.base_color,
            ),
            Cylinder(
                radius=0.015,
                height=pole_h,
                segments=6,
                transform=Transform.at(0, base_h + pole_h / 2, 0),
                color=self.base_color,
            ),
            Cylinder(
                radius=0.17,
                height=shade_h,
                segments=8,
                transform=Transform.at(0, base_h + pole_h + shade_h / 2, 0),
                color=self.shade_color,
            ),
        ]
