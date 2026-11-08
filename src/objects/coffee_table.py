from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform, texturize
from src.objects.components import Block

@dataclass
class CoffeeTable(Group):
    surface = True

    width: float = 0.9
    depth: float = 0.5
    height: float = 0.42
    top_thickness: float = 0.04
    leg_thickness: float = 0.05
    top_color: Color = field(default_factory=lambda: Color(0.55, 0.32, 0.15, 1))
    leg_color: Color = field(default_factory=lambda: Color(0.42, 0.22, 0.1, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.width, self.depth, self.height, self.top_thickness) <= 0:
            raise ValueError("CoffeeTable sizes should be positive")

        inset = 0.03
        t = self.leg_thickness
        leg_h = self.height - self.top_thickness
        leg_x = self.width / 2 - inset - t / 2
        leg_z = self.depth / 2 - inset - t / 2
        if leg_x <= 0 or leg_z <= 0 or leg_h <= 0.15:
            raise ValueError("CoffeeTable doesn't fit its legs")

        shelf_t = 0.02
        shelf_y = 0.12

        self.parts = [
            *[
                Block(width=t, height=leg_h, depth=t, transform=Transform.at(x, leg_h / 2, z), color=self.leg_color)
                for x in(-leg_x, leg_x)
                for z in (-leg_z, leg_z)
            ],

            Block(width=2 * leg_x - t, height=shelf_t, depth=2 * leg_z - t, transform=Transform.at(0, shelf_y, 0), color=self.leg_color),

            Block(width=self.width, height=self.top_thickness, depth=self.depth, transform=Transform.at(0, leg_h + self.top_thickness / 2, 0), color=self.top_color),
        ]

        texturize(self.parts, "madeira_clara.png", 0.4)
