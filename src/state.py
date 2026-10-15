from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import *

from src.objects import Object
from src.objects.block import Block
from src.objects.triangle import Triangle
from src.camera import Camera


class State:
    window: _Pointer[
        glfw._GLFWwindow
    ]  # precisa do __future__ annotations para deixar selecionar o tipo sem dar pau na 3.8

    def __init__(self) -> None:
        self.objects: list[
            Object
        ] = []  # gambiarra do momento: lista de ids de objetos para serem renderizados em outra camada
        self.camera = Camera(position=(0.0,0.5,2.0), pitch=-15)

    def update(self):
        pass

    def load_objects(self):
        self.objects.append(Block())
