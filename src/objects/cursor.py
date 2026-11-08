from dataclasses import dataclass

from src.objects import COLORS, Color, Group, Transform
from src.objects.components import Block

CURSOR_SIZE = 1
CURSOR_HEIGHT = 0.04
CURSOR_GRID_STEP = 1.0


@dataclass
class Cursor(Group):
    def __post_init__(self) -> None:

        cursor = Block(
            width=CURSOR_SIZE,
            height=CURSOR_HEIGHT,
            depth=CURSOR_SIZE,
            transform=Transform.at(0, CURSOR_HEIGHT / 2, 0),
            color=Color(0, 0.5, 0, 0.5),
            self_shadow_enabled=False,
        )

        self.parts = [cursor]
