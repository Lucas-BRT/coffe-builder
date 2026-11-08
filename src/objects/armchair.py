from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block

@dataclass
class Armchair(Group):
    width: float = 0.7
    depth: float = 0.65
    frame_color: Color = field(default_factory=lambda: Color(0.42, 0.22, 0.1, 1))
    fabric_color: Color = field(default_factory=lambda: Color(0.1, 0.6, 0.58, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.width, self.depth) <=0.4:
            raise ValueError("Armchair is too small")

        w, d = self.width, self.depth
        foot_h = 0.05      # pés
        body_y = foot_h    # onde o estofado começa
        arm_w = 0.1        # espessura dos braços
        arm_h = 0.5        # altura dos braços
        back_t = 0.1       # espessura do encosto
        back_h = 0.65      # altura do encosto
        seat_base_h = 0.2  # corpo embaixo da almofada
        cushion_h = 0.1

        inner_w = w - 2 * arm_w
        seat_d = d - back_t
        seat_z = back_t / 2

        def lighter(c: Color, k: float = 1.15) -> Color:
            return Color(min(1.0, c.r * k), min(1.0, c.g * k), min(1.0, c.b * k), 1)

        feet: List[Entity] = [
            Block(width=0.06, height=foot_h, depth=0.06,
                  transform=Transform.at(x, foot_h / 2, z), color=self.frame_color)
            for x in (-w / 2 + 0.06, w / 2 - 0.06)
            for z in (-d / 2 + 0.06, d / 2 - 0.06)
        ]

        self.parts = [
            *feet,
            # braços: vão do estofado até o topo
            *[
                Block(width=arm_w, height=arm_h, depth=d,
                      transform=Transform.at(x, body_y + arm_h / 2, 0),
                      color=self.fabric_color)
                for x in (-w / 2 + arm_w / 2, w / 2 - arm_w / 2)
            ],
            # encosto
            Block(width=inner_w, height=back_h, depth=back_t,
                  transform=Transform.at(0, body_y + back_h / 2, -d / 2 + back_t / 2),
                  color=self.fabric_color),
            # corpo embaixo do assento
            Block(width=inner_w, height=seat_base_h, depth=seat_d,
                  transform=Transform.at(0, body_y + seat_base_h / 2, seat_z),
                  color=self.fabric_color),
            # almofada do assento
            Block(width=inner_w, height=cushion_h, depth=seat_d,
                  transform=Transform.at(0, body_y + seat_base_h + cushion_h / 2, seat_z),
                  color=lighter(self.fabric_color)),
            # almofada do encosto
            Block(width=inner_w * 0.85, height=0.3, depth=0.06,
                  transform=Transform.at(
                      0, body_y + seat_base_h + cushion_h + 0.15, -d / 2 + back_t + 0.03),
                  color=lighter(self.fabric_color)),
        ]
