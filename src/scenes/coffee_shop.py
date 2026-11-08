from __future__ import annotations

from typing import List

from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.armchair import Armchair
from src.objects.cafe_chair import CafeChair
from src.objects.coffee_machine import CoffeeMachine
from src.objects.coffee_table import CoffeeTable
from src.objects.components import Block
from src.objects.cup import Cup
from src.objects.floor_lamp import FloorLamp
from src.objects.L_counter import LCounter
from src.objects.menu import Menu
from src.objects.round_table import RoundTable
from src.scenes import Scene
from src.texture import Texture

ROOM_SIZE = 6.0
WALL_HEIGHT = 2.4
WALL_THICKNESS = 0.1
FLOOR_THICKNESS = 0.05

FLOOR_COLOR = Color(0.85, 0.55, 0.28, 1)  # madeira cor de mel
BACK_WALL_COLOR = Color(0.1, 0.6, 0.58, 1)  # verde-azulado
SIDE_WALL_COLOR = Color(0.96, 0.72, 0.2, 1)  # mostarda
LIGHT_COLOR = Color(1.0, 0.86, 0.62, 1)

# astro que ilumina a sala de longe: sol de dia, lua (mais fraca e azulada) de noite
SUN_POSITION = (40.0, 50.0, 40.0)
SUN_INTENSITY = 0.35
MOON_COLOR = Color(0.5, 0.62, 1.0, 1)
MOON_POSITION = (-40.0, 45.0, -30.0)
MOON_INTENSITY = 0.12

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
    table = RoundTable(top_color=TABLE_TOP_COLOR, leg_color=WOOD_COLOR)
    # centro da cadeira até o centro da mesa: metade da mesa + metade do
    # assento, menos um pouco para a cadeira ficar "enfiada" embaixo do tampo
    distance = table.width / 2 + 0.21 - 0.06

    def chair(transform: Transform) -> CafeChair:
        return CafeChair(
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

        self.light = Block(
            width=0.35,
            height=0.35,
            depth=0.35,
            transform=Transform.at(*SUN_POSITION),
            color=LIGHT_COLOR,
            emissive=True,
        )
        self.objects.append(self.light)
        self.sky_intensity = SUN_INTENSITY
        self.night = False

        self.objects.append(
            Block(
                width=ROOM_SIZE,
                height=FLOOR_THICKNESS,
                depth=ROOM_SIZE,
                transform=Transform.at(0, -FLOOR_THICKNESS / 2, 0),
                color=COLORS["WHITE"],
                grid_enabled=True,
                texture=Texture("madeira.png"),
                uv_tile=1.0,
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

        # luz, chão e paredes ficam fixos
        for structure in self.objects:
            structure.selectable = False

        counter = LCounter(transform=Transform.at(-1.2, 0, -1.9))
        counter.parts += [
            CoffeeMachine(transform=Transform.at(0.7, counter.height, -0.1)),
            Cup(transform=Transform.at(0.0, counter.height, 0.1)),
            Cup(transform=Transform.at(-0.35, counter.height, 0.05, ry=40)),
        ]
        self.objects.append(counter)
        self.objects.append(FloorLamp(transform=Transform.at(-2.6, 0, 2.4)))
        self.objects.append(Menu(transform=Transform.at(-1.2, 0, -half + 0.04 / 2)))

        # 4 mesas em grade 2x2 na parte da frente da sala
        positions = [(x, z) for x in (-1.5, 1.5) for z in (-0.2, 1.9) if (x, z) != (1.5, 1.9)]
        for (x, z), seat_color in zip(positions, SEAT_COLORS):
            self.objects.append(dining_set(x, z, seat_color))

        self.objects.append(CoffeeTable(transform=Transform.at(1.5, 0, 1.9)))
        self.objects.append(Armchair(transform=Transform.at(0.7, 0, 1.9, ry=90)))
        self.objects.append(Armchair(transform=Transform.at(2.3, 0, 1.9, ry=-90)))

    def toggle_night(self) -> None:
        """Troca o sol pela lua e vice-versa"""
        self.night = not self.night
        self.light.color = MOON_COLOR if self.night else LIGHT_COLOR
        self.light.move_to(*(MOON_POSITION if self.night else SUN_POSITION))
        self.sky_intensity = MOON_INTENSITY if self.night else SUN_INTENSITY
