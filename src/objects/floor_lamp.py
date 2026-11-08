from dataclasses import dataclass, field
from typing import List, cast

from src.objects import COLORS, Color, Entity, Group, Transform
from pyglm import glm

from src.objects.components import Cylinder

@dataclass
class FloorLamp(Group):
    # a Scene procura Entities com emits_light para montar a lista de luzes
    emits_light = True

    height: float = 1.6
    base_color: Color = field(default_factory=lambda: COLORS["DARK_GRAY"])
    shade_color: Color = field(default_factory=lambda: Color(0.98, 0.85, 0.5, 1))
    off_shade_color: Color = field(default_factory=lambda: Color(0.45, 0.4, 0.28, 1))
    light_color: Color = field(default_factory=lambda: Color(1.0, 0.85, 0.55, 1))
    # luz de perto não precisa de muita força: a atenuação quase não atua
    light_intensity: float = 0.3
    on: bool = True

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        base_h = 0.03
        shade_h = 0.22
        pole_h = self.height - base_h - shade_h
        if pole_h <= 0:
            raise ValueError("FloorLamp is too short")

        # a luz sai logo abaixo da cúpula, para iluminar a haste e o chão
        self.light_offset = glm.vec3(0, self.height - shade_h - 0.02, 0)
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
        self.shade = cast(Cylinder, self.parts[-1])
        self._apply_state()

    def toggle(self) -> None:
        self.on = not self.on
        self._apply_state()

    def _apply_state(self) -> None:
        self.shade.emissive = self.on
        self.shade.color = self.shade_color if self.on else self.off_shade_color
