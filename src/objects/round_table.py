from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Cylinder

@dataclass
class RoundTable(Group):
    radius: float = 0.45
    height: float = 0.75
    top_thickness: float = 0.04
    top_color: Color = field(default_factory=lambda: Color(0.98, 0.93, 0.82, 1))
    leg_color: Color = field(default_factory=lambda: COLORS["DARK_GRAY"])

    parts: List[Entity] = field(init=False)

    @property
    def width(self) -> float:
        return 2 * self.radius

    @property
    def depth(self) -> float:
        return 2 * self.radius

    def __post_init__(self) -> None:
        if min(self.radius, self.height, self.top_thickness) <= 0:
            raise ValueError("RoundTable sizes should be positive")

        base_h = 0.03
        column_h = self.height -self.top_thickness - base_h

        if column_h <= 0:
            raise ValueError("RoundTable is too short")

        self.parts = [
            # base no chão
            Cylinder(radius=self.radius * 0.5, height=base_h, segments=12, transform=Transform.at(0, base_h / 2, 0), color=self.leg_color),
            # coluna central
            Cylinder(radius=0.04, height=column_h, segments=8, transform=Transform.at(0, base_h + column_h / 2, 0), color=self.leg_color),
            # mesa
            Cylinder(radius=self.radius, height=self.top_thickness, segments=12, transform=Transform.at(0, self.height - self.top_thickness / 2, 0), color=self.top_color),
        ]
