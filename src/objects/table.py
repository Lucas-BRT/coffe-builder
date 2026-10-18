from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block


@dataclass
class Table(Group):
    """Mesa de 4 pés, montada com Blocks. Medidas em metros.

    A origem fica no chão, embaixo do centro do tampo.

    width:         tamanho do tampo no eixo X
    depth:         tamanho do tampo no eixo Z
    height:        altura do chão até o topo do tampo
    leg_thickness: espessura dos pés
    leg_inset:     quanto os pés ficam recuados da borda do tampo
    """

    width: float = 0.8
    depth: float = 0.8
    height: float = 0.75
    top_thickness: float = 0.04
    leg_thickness: float = 0.06
    leg_inset: float = 0.04
    top_color: Color = field(default_factory=lambda: COLORS["LIGHT_BROWN"])
    leg_color: Color = field(default_factory=lambda: COLORS["BROWN"])

    # Redefine o campo do pai: a Table monta as partes sozinha, então elas
    # não entram mais no __init__.
    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.width, self.depth, self.height, self.top_thickness) <= 0:
            raise ValueError("Table sizes should be positive")

        leg_height = self.height - self.top_thickness
        leg_x = self.width / 2 - self.leg_inset - self.leg_thickness / 2
        leg_z = self.depth / 2 - self.leg_inset - self.leg_thickness / 2
        if leg_x <= 0 or leg_z <= 0:
            raise ValueError("Legs don't fit under this table top")

        legs: List[Entity] = [
            Block(
                width=self.leg_thickness,
                height=leg_height,
                depth=self.leg_thickness,
                transform=Transform.at(x, leg_height / 2, z),
                color=self.leg_color,
            )
            for x in (-leg_x, leg_x)
            for z in (-leg_z, leg_z)
        ]
        top = Block(
            width=self.width,
            height=self.top_thickness,
            depth=self.depth,
            transform=Transform.at(0, leg_height + self.top_thickness / 2, 0),
            color=self.top_color,
        )
        self.parts = [*legs, top]
