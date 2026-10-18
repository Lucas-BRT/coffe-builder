from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block


@dataclass
class Counter(Group):
    """Bancada / balcão: corpo fechado, tampo que sobra um pouco nas bordas e
    rodapé recuado. Medidas em metros.

    A origem fica no chão, embaixo do centro do balcão. A frente (lado do
    cliente) aponta para +Z, igual a Chair.

    length:   comprimento no eixo X
    height:   altura do chão até o topo do tampo
    depth:    profundidade do corpo no eixo Z
    overhang: quanto o tampo passa do corpo em cada borda
    """

    length: float = 2.0
    height: float = 1.0
    depth: float = 0.6
    top_thickness: float = 0.05
    overhang: float = 0.03
    plinth_height: float = 0.1
    body_color: Color = field(default_factory=lambda: COLORS["BROWN"])
    top_color: Color = field(default_factory=lambda: COLORS["LIGHT_GRAY"])
    plinth_color: Color = field(default_factory=lambda: COLORS["DARK_GRAY"])

    # Redefine o campo do pai: o Counter monta as partes sozinho, então elas
    # não entram mais no __init__.
    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.length, self.height, self.depth, self.top_thickness) <= 0:
            raise ValueError("Counter sizes should be positive")
        body_height = self.height - self.top_thickness - self.plinth_height
        if body_height <= 0:
            raise ValueError("Counter is too short for its top and plinth")

        # rodapé recuado na frente, como em armário de cozinha
        plinth_recess = 0.05
        plinth = Block(
            width=self.length,
            height=self.plinth_height,
            depth=self.depth - plinth_recess,
            transform=Transform.at(0, self.plinth_height / 2, -plinth_recess / 2),
            color=self.plinth_color,
        )
        body = Block(
            width=self.length,
            height=body_height,
            depth=self.depth,
            transform=Transform.at(0, self.plinth_height + body_height / 2, 0),
            color=self.body_color,
        )
        top = Block(
            width=self.length + 2 * self.overhang,
            height=self.top_thickness,
            depth=self.depth + 2 * self.overhang,
            transform=Transform.at(0, self.height - self.top_thickness / 2, 0),
            color=self.top_color,
        )
        self.parts = [plinth, body, top]

