from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block, Cylinder

@dataclass
class CoffeeMachine(Group):
    prop = True

    width: float = 0.5
    depth: float = 0.32
    height: float = 0.36
    body_color: Color = field(default_factory=lambda: Color(0.93, 0.88, 0.78, 1))
    accent_color: Color = field(default_factory=lambda: COLORS["DARK_GRAY"])
    knob_color: Color = field(default_factory=lambda: Color(0.78, 0.2, 0.18, 1))
    tank_color: Color = field(default_factory=lambda: Color(0.6, 0.8, 0.95, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.width, self.depth, self.height) <= 0:
            raise ValueError("CoffeeMachine sizes should be positive")

        tray_h = 0.03
        top_h = 0.02
        body_h = self.height - tray_h - top_h
        if body_h <= 0.25:
            raise ValueError("CoffeeMachine is too short")
        front = self.depth / 2  # z da face da frente do corpo
        top_y = tray_h + body_h + top_h  # topo da máquina (sem o reservatório)

        steel = Color(0.72, 0.74, 0.78, 1)
        handle = Color(0.2, 0.12, 0.08, 1)

        def knob(x: float, y: float, radius: float, color: Color) -> Cylinder:
            return Cylinder(
                radius = radius,
                height=0.025,
                segments=8,
                transform=Transform.at(x,y, front + 0.012, rx=90),
                color = color,
            )

        head_y = tray_h + 0.2
        basket_z = front + 0.05

        self.parts = [
            #bandeija
            Block(width=self.width,
                height=tray_h,
                depth=self.depth + 0.08,
                transform=Transform.at(0, tray_h / 2, 0.04),
                color=self.accent_color,
            ),
            #corpo
            Block(
                width=self.width,
                height=body_h,
                depth=self.depth,
                transform=Transform.at(0, tray_h + body_h / 2, 0),
                color=self.body_color,
            ),
            #tampo
            Block(
                width=self.width + 0.02,
                height=top_h,
                depth=self.depth + 0.02,
                transform=Transform.at(0, tray_h + body_h + top_h / 2, 0),
                color=self.accent_color,
            ),
            #reservatorio
            Block(
                width=self.width * 0.45,
                height=0.12,
                depth=self.depth * 0.5,
                transform=Transform.at(
                    -self.width * 0.22, top_y + 0.06, -self.depth * 0.18
                ),
                color=self.tank_color,
            ),

            Block(
                width=0.14,
                height=0.06,
                depth=0.07,
                transform=Transform.at(0, head_y, front + 0.035),
                color=steel,
            ),
            #porta filtro
            Cylinder(
                radius=0.04,
                height=0.03,
                segments=8,
                transform=Transform.at(0, head_y - 0.045, basket_z),
                color=self.accent_color,
            ),
            # cabo do porta filtro
            Block(
                width=0.025,
                height=0.022,
                depth=0.11,
                transform=Transform.at(0, head_y - 0.045, basket_z + 0.085),
                color=handle,
            ),
            #botoes
            knob(0, tray_h + body_h - 0.04, 0.03, COLORS["WHITE"]),
            knob(-0.15, tray_h + body_h - 0.04, 0.022, self.knob_color),
            knob(0.15, tray_h + body_h - 0.04, 0.022, self.knob_color),

            #lanca vapor
            Block(
                width=0.014,
                height=0.014,
                depth=0.045,
                transform=Transform.at(
                    self.width / 2 - 0.05, head_y + 0.02, front + 0.02
                ),
                color=steel,
            ),
            Block(
                width=0.014,
                height=0.15,
                depth=0.014,
                transform=Transform.at(
                    self.width / 2 - 0.05, head_y - 0.055, front + 0.04
                ),
                color=steel,
            ),
        ]
