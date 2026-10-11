from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import *

from src.objects import Object
from src.objects.block import Block
from src.objects.triangle import Triangle


class State:
    window: _Pointer[
        glfw._GLFWwindow
    ]  # precisa do __future__ annotations para deixar selecionar o tipo sem dar pau na 3.8

    def __init__(self) -> None:
        self.objects: list[
            Object
        ] = []  # gambiarra do momento: lista de ids de objetos para serem renderizados em outra camada

    def update(self):

        print(f"{len(self.objects)} objetos na aplicação")

        for object in self.objects:
            object.rotate(
                0.01,
                x_angle=-glfw.get_time(),
                y_angle=-glfw.get_time(),
                z_angle=-glfw.get_time(),
            )

    def load_objects(self):
        # self.objects.append(Triangle(-0.5, 0.0))
        # self.objects.append(Triangle(0.0, 0.0))
        # self.objects.append(Square(x=0.0, y=0.0))
        self.objects.append(Block(width=0.25, height=0.75))
