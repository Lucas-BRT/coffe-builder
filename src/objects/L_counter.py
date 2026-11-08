from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block

@dataclass
class LCounter(Group):
    length: float = 3.0
    wing: float = 1.4
    height: float = 1.0
    depth: float = 0.6
    top_thickness: float = 0.05
    overhang: float = 0.03
    plinth_height: float = 0.1
    body_color: Color = field(default_factory=lambda: Color(0.78, 0.2, 0.18, 1))
    top_color: Color = field(default_factory=lambda: Color(0.97, 0.95, 0.9, 1))
    plinth_color: Color = field(default_factory=lambda: Color(0.2, 0.12, 0.08, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.length, self.wing, self.height, self.depth, self.top_thickness) <= 0:
            raise ValueError("LCounter sizes should be positive")

        L, W, D, o = self.length, self.wing, self.depth, self.overhang
        ph, tt = self.plinth_height, self.top_thickness
        wing_x = L / 2 - D / 2          # centro da ala no eixo X
        wing_z = D / 2 + W / 2          # centro da ala no eixo Z
        top_y = self.height - tt / 2
        body_h = self.height - self.top_thickness - self.plinth_height

        self.parts = [
            #rodape
            Block(width=L - 0.05, height=ph, depth=D - 0.05,transform=Transform.at(-0.025, ph / 2, -0.025), color=self.plinth_color),
            Block(width=D - 0.05, height=ph, depth=W, transform=Transform.at(wing_x, ph / 2, D / 2 - 0.05 + W / 2), color=self.plinth_color),

            #corpo
            Block(width=L, height=body_h, depth=D, transform=Transform.at(0, ph + body_h / 2, 0), color=self.body_color),
            Block(width=D, height=body_h, depth=W, transform=Transform.at(wing_x, ph + body_h / 2, wing_z), color=self.body_color),

            #mesa
            Block(width=L + 2 * o, height=tt, depth=D + 2 * o,transform=Transform.at(0, top_y, 0), color=self.top_color),
            Block(width=D + 2 * o, height=tt, depth=W, transform=Transform.at(wing_x + 0.0, top_y, D / 2 + o + W / 2), color=self.top_color),
        ]
