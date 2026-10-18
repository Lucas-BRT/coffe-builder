from __future__ import annotations

from typing import List

from src.objects import Color, Entity, Group, Transform
from src.objects.chair import Chair
from src.objects.components import Block
from src.objects.counter import Counter
from src.objects.table import Table
from src.scenes import Scene

ROOM_SIZE = 6.0
WALL_HEIGHT = 2.4
WALL_THICKNESS = 0.1
FLOOR_THICKNESS = 0.05

FLOOR_COLOR = Color(0.85, 0.55, 0.28, 1)  # madeira cor de mel
BACK_WALL_COLOR = Color(0.1, 0.6, 0.58, 1)  # verde-azulado
SIDE_WALL_COLOR = Color(0.96, 0.72, 0.2, 1)  # mostarda

COUNTER_BODY_COLOR = Color(0.78, 0.2, 0.18, 1)  # vermelho tijolo
COUNTER_TOP_COLOR = Color(0.97, 0.95, 0.9, 1)  # mármore claro
COUNTER_PLINTH_COLOR = Color(0.2, 0.12, 0.08, 1)

TABLE_TOP_COLOR = Color(0.98, 0.93, 0.82, 1)
WOOD_COLOR = Color(0.42, 0.22, 0.1, 1)  # estrutura de mesas e cadeiras

# cada conjunto de mesa ganha uma cor de assento diferente
SEAT_COLORS = [
    Color(0.95, 0.35, 0.3, 1),  # coral
    Color(0.2, 0.55, 0.9, 1),  # azul
    Color(0.98, 0.78, 0.15, 1),  # amarelo
    Color(0.35, 0.75, 0.35, 1),  # verde
]


def dining_set(x: float, z: float, seat_color: Color) -> Group:
    """Uma mesa com 4 cadeiras viradas para ela, uma de cada lado"""
    table = Table(top_color=TABLE_TOP_COLOR, leg_color=WOOD_COLOR)
    # centro da cadeira até o centro da mesa: metade da mesa + metade do
    # assento, menos um pouco para a cadeira ficar "enfiada" embaixo do tampo
    distance = table.width / 2 + 0.21 - 0.06

    def chair(transform: Transform) -> Chair:
        return Chair(
            transform=transform, frame_color=WOOD_COLOR, seat_color=seat_color
        )

    chairs: List[Entity] = [
        chair(Transform.at(0, 0, -distance)),
        chair(Transform.at(0, 0, distance, ry=180)),
        chair(Transform.at(-distance, 0, 0, ry=90)),
        chair(Transform.at(distance, 0, 0, ry=-90)),
    ]
    return Group(parts=[table, *chairs], transform=Transform.at(x, 0, z))


class CoffeeShopScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.iso_zoom = 4.5

        half = ROOM_SIZE / 2

        self.objects.append(
            Block(
                width=ROOM_SIZE,
                height=FLOOR_THICKNESS,
                depth=ROOM_SIZE,
                transform=Transform.at(0, -FLOOR_THICKNESS / 2, 0),
                color=FLOOR_COLOR,
            )
        )

        self.objects += [
            Block(
                width=ROOM_SIZE + WALL_THICKNESS,
                height=WALL_HEIGHT,
                depth=WALL_THICKNESS,
                transform=Transform.at(
                    -WALL_THICKNESS / 2, WALL_HEIGHT / 2, -half - WALL_THICKNESS / 2
                ),
                color=BACK_WALL_COLOR,
            ),
            Block(
                width=WALL_THICKNESS,
                height=WALL_HEIGHT,
                depth=ROOM_SIZE,
                transform=Transform.at(-half - WALL_THICKNESS / 2, WALL_HEIGHT / 2, 0),
                color=SIDE_WALL_COLOR,
            ),
        ]

        self.objects.append(
            Counter(
                length=3.0,
                transform=Transform.at(-1.2, 0, -1.9),
                body_color=COUNTER_BODY_COLOR,
                top_color=COUNTER_TOP_COLOR,
                plinth_color=COUNTER_PLINTH_COLOR,
            )
        )

        # 4 mesas em grade 2x2 na parte da frente da sala
        positions = [(x, z) for x in (-1.5, 1.5) for z in (-0.2, 1.9)]
        for (x, z), seat_color in zip(positions, SEAT_COLORS):
            self.objects.append(dining_set(x, z, seat_color))
