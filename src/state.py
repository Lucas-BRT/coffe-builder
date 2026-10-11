from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import *

from src.objects import Object
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

        # self.objects[0].rotate(0.01, z_angle=-glfw.get_time())

        # for index, object in enumerate(self.objects):
        #     mutation = self.time + index
        #     print(mutation)
        #     object.rotate(0.01, mutation, z_angle=mutation)
        #     if index == 0:
        #         object.translate(cos(self.time))

        pass

    def load_objects(self):
        # self.objects.append(Triangle(-0.5, 0.0))
        self.objects.append(Triangle(0.0, 0.0))
        # self.objects.append(Square(x=0.0, y=0.0))
