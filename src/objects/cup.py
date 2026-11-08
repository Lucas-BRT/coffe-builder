from dataclasses import dataclass, field
from typing import List

from src.objects import Color, Entity, Group, Transform
from src.objects.components import Block, Cylinder

@dataclass
class Cup(Group):
    prop = True

    radius: float = 0.04
    height: float = 0.06
    cup_color: Color = field(default_factory=lambda: Color(0.97, 0.95, 0.9, 1))
    coffee_color: Color = field(default_factory=lambda: Color(0.25, 0.13, 0.07, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.radius, self.height) <= 0:
            raise ValueError("Cup sizes should be positive")

        saucer_h = 0.008
        top = saucer_h + self.height

        self.parts = [
            Cylinder(
                radius=self.radius * 1.8,
                height=saucer_h,
                segments=8,
                transform=Transform.at(0, saucer_h / 2, 0),
                color=self.cup_color,
            ),
            Cylinder(
                radius=self.radius,
                height=self.height,
                segments=8,
                transform=Transform.at(0, saucer_h + self.height / 2, 0),
                color=self.cup_color,
            ),
            #café
             Cylinder(
                 radius=self.radius * 0.82,
                 height=0.004,
                 segments=8,
                 transform=Transform.at(0, top + 0.001, 0),
                 color=self.coffee_color,
            ),
            # asa
            Block(
                width=0.03,
                height=0.012,
                depth=0.012,
                transform=Transform.at(
                    self.radius + 0.012, saucer_h + self.height * 0.55, 0
                ),
                color=self.cup_color,
            ),
        ]
