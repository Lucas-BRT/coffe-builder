from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform, texturize
from src.objects.components import Block, Cylinder

@dataclass
class CafeChair(Group):
    seat_radius: float = 0.21
    seat_height: float = 0.45
    backrest_height: float = 0.4
    leg_thickness: float = 0.035
    frame_color: Color = field(default_factory=lambda: Color(0.42, 0.22, 0.1, 1))
    seat_color: Color = field(default_factory=lambda: Color(0.95, 0.35, 0.3, 1))

    parts: List[Entity] =field(init=False)

    def __post_init__(self) -> None:
        if min(self.seat_radius, self.seat_height, self.backrest_height) <= 0:
            raise ValueError("CafeChair sizes should be positive")

        t = self.leg_thickness
        seat_t = 0.04
        frame_t = 0.03
        leg_h = self.seat_height - seat_t - frame_t
        corner = self.seat_radius * 0.62
        back_z = -corner
        top = self.seat_height + self.backrest_height

        front_legs: List[Entity] = [
            Block(width=t, height=leg_h, depth=t, transform=Transform.at(x, leg_h / 2, corner), color=self.frame_color)
            for x in (-corner, corner)
        ]

        back_h = top -0.02
        back_posts: List[Entity] = [
            Block(width=t, height=back_h, depth=t, transform=Transform.at(x, back_h / 2, back_z), color=self.frame_color)
            for x in (-corner, corner)
        ]

        rail_y = leg_h * 0.35
        rails: List[Entity] = [
            Block(width=2 * corner, height=0.02, depth=0.02, transform=Transform.at(0, rail_y, z), color=self.frame_color)
            for z in (-corner, corner)

        ] + [
            Block(width=0.02, height=0.02, depth=2 * corner, transform=Transform.at(x, rail_y, 0), color=self.frame_color)
            for x in (-corner, corner)
        ]

        rail_w = 2 * corner
        self.parts = [
            *front_legs,
            *back_posts,
            *rails,
            #madeira embaixo do assento
            Cylinder(radius=self.seat_radius * 0.95, height=frame_t, segments=8,transform=Transform.at(0, leg_h + frame_t / 2, 0),color=self.frame_color),
            # assento colorido
            Cylinder(radius=self.seat_radius, height=seat_t, segments=8,transform=Transform.at(0, leg_h + frame_t + seat_t / 2, 0),color=self.seat_color),
            #encosto
            Block(width=rail_w + t, height=0.07, depth=0.03,transform=Transform.at(0, top - 0.055, back_z), color=self.frame_color),
            Block(width=rail_w, height=0.03, depth=0.02,transform=Transform.at(0, self.seat_height + self.backrest_height * 0.35, back_z),color=self.frame_color),
            Block(width=0.04, height=self.backrest_height * 0.7, depth=0.02,transform=Transform.at(0, self.seat_height + self.backrest_height * 0.35 + 0.1, back_z),color=self.frame_color),
        ]

        texturize(self.parts, "madeira_clara.png", 0.3, self.frame_color)
        texturize(self.parts, "tecido.png", 0.2, self.seat_color)
