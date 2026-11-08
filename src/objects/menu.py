from dataclasses import dataclass, field
from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block

@dataclass
class Menu(Group):
    width: float = 1.4
    height: float = 0.75
    depth: float = 0.04
    mount_height: float = 1.55
    frame_color: Color = field(default_factory=lambda: Color(0.42, 0.22, 0.1, 1))
    board_color: Color = field(default_factory=lambda: Color(0.13, 0.15, 0.14, 1))
    chalk_color: Color = field(default_factory=lambda: Color(0.95, 0.95, 0.88, 1))
    title_color: Color = field(default_factory=lambda: Color(0.98, 0.8, 0.35, 1))

    parts: List[Entity] = field(init=False)

    def __post_init__(self) -> None:
        if min(self.width, self.height, self.depth) <= 0:
            raise ValueError("MenuBoard sizes should be positive")

        w, h, d, t = self.width, self.height, self.depth, 0.05

        if w <= 4 * t or h <= 4 * t:
            raise ValueError("MenuBoard is too small")

        cy = self.mount_height
        inner_w, inner_h = w - 2 * t, h - 2 * t

        recess = 0.015
        panel_front = d / 2 - recess
        chalk_z = panel_front + 0.002

        def chalk(x: float, y: float, line_w: float, line_h: float, color: Color) -> Block:
            return Block(
                width=line_w,
                height=line_h,
                depth=0.004,
                transform=Transform.at(x, cy + y, chalk_z),
                color=color,
            )

        parts: List[Entity] = [
            #moldura
            Block(width=w, height=t, depth=d, transform=Transform.at(0, cy+h/2 - t/2, 0), color=self.frame_color),
            Block(width=w, height=t, depth=d, transform=Transform.at(0, cy+h/2 - t/2, 0), color=self.frame_color),
            Block(width=t, height=inner_h, depth=d, transform=Transform.at(-w / 2 + t / 2, cy, 0), color=self.frame_color),
            Block(width=t, height=inner_h, depth=d, transform=Transform.at(-w / 2 + t / 2, cy, 0), color=self.frame_color),

            #lousa
            Block(width=inner_w, height=inner_h, depth=d - recess, transform=Transform.at(0, cy, -recess / 2), color = self.board_color),

            #titulo
            chalk(0, inner_h / 2 - 0.09, inner_w * 0.4, 0.05, self.title_color),
            chalk(0, inner_h / 2 - 0.15, inner_w * 0.55, 0.008, self.title_color),
        ]

        #item e preco
        name_widths = [0.55, 0.42, 0.6, 0.48, 0.38]
        left = -inner_w / 2 + 0.1
        right = inner_w / 2 - 0.1
        top_row = inner_h / 2 - 0.26
        row_gap = (inner_h - 0.36) / max(len(name_widths) - 1, 1)
        for i, line_w in enumerate(name_widths):
            y = top_row - i * min(row_gap, 0.1)
            parts.append(chalk(left + line_w / 2, y, line_w * inner_w / 1.2, 0.025, self.chalk_color))
            parts.append(chalk(right - 0.05, y, 0.1, 0.025, self.chalk_color))

        self.parts = parts
