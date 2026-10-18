from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block


@dataclass
class Chair(Group):
    """Cadeira com encosto, montada com Blocks. Medidas em metros.

    A origem fica no chão, embaixo do centro do assento. A frente (onde a
    pessoa senta) aponta para +Z e o encosto fica em -Z, então para virar a
    cadeira para outro lado é só girar em Y.

    seat_size:       largura e profundidade do assento
    seat_height:     altura do chão até o topo do assento
    backrest_height: altura do encosto, medida a partir do assento
    leg_thickness:   espessura dos pés e do encosto
    """

    seat_size: float = 0.42
    seat_height: float = 0.45
    backrest_height: float = 0.4
    leg_thickness: float = 0.04
    frame_color: Color = field(default_factory=lambda: COLORS["BROWN"])
    seat_color: Color = field(default_factory=lambda: COLORS["LIGHT_BROWN"])

    # Redefine o campo do pai: a Chair monta as partes sozinha, então elas
    # não entram mais no __init__.
    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.seat_size, self.seat_height, self.backrest_height) <= 0:
            raise ValueError("Chair sizes should be positive")
        if self.leg_thickness * 2 >= self.seat_size:
            raise ValueError("Legs are too thick for this seat")

        seat_thickness = 0.04
        leg_height = self.seat_height - seat_thickness
        # centro dos pés, encostados nos cantos do assento
        corner = self.seat_size / 2 - self.leg_thickness / 2

        legs: List[Entity] = [
            Block(
                width=self.leg_thickness,
                height=leg_height,
                depth=self.leg_thickness,
                transform=Transform.at(x, leg_height / 2, z),
                color=self.frame_color,
            )
            for x in (-corner, corner)
            for z in (-corner, corner)
        ]
        seat = Block(
            width=self.seat_size,
            height=seat_thickness,
            depth=self.seat_size,
            transform=Transform.at(0, leg_height + seat_thickness / 2, 0),
            color=self.seat_color,
        )
        backrest = Block(
            width=self.seat_size,
            height=self.backrest_height,
            depth=self.leg_thickness,
            transform=Transform.at(
                0, self.seat_height + self.backrest_height / 2, -corner
            ),
            color=self.frame_color,
        )
        self.parts = [*legs, seat, backrest]
