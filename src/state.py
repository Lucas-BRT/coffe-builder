from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import *

from src.config import Config
from src.objects import Object
from src.objects.block import Block
from src.objects.triangle import Triangle
from src.renderer import Camera


class State:
    window: _Pointer[
        glfw._GLFWwindow
    ]  # precisa do __future__ annotations para deixar selecionar o tipo sem dar pau na 3.8

    def __init__(self, config: Config) -> None:
        self.objects: list[
            Object
        ] = []  # gambiarra do momento: lista de ids de objetos para serem renderizados em outra camada
        self.rotate = False
        self.config = config

    def set_camera(self, renderer: Camera):
        self.camera = renderer

    def update(self):

        print(f"{len(self.objects)} objetos na aplicação")

        for object in self.objects:
            if self.rotate:
                self.camera.rotate(
                    0.01,
                    # x_angle=-glfw.get_time(),
                    y_angle=glfw.get_time(),
                    # z_angle=-glfw.get_time(),
                )

    def load_objects(self):
        self.objects.append(Triangle(-0.5, 0.0))
        # self.objects.append(Triangle(0.0, 0.0))
        # self.objects.append(Square(x=0.0, y=0.0))
        self.objects.append(Block(width=0.25, height=0.75))
