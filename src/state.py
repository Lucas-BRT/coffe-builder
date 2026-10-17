from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import *

from src.camera import Camera, IsometricCamera
from src.config import Config
from src.objects import Object
from src.objects.chair import Chair
from src.objects.components.block import Block
from src.objects.components.triangle import Triangle
from src.scenes import Scene
from src.scenes.TestCoffe import TestCoffe


class State:
    window: _Pointer[
        glfw._GLFWwindow
    ]  # precisa do __future__ annotations para deixar selecionar o tipo sem dar pau na 3.8

    def __init__(self, config: Config) -> None:
        self.objects: list[
            Object
        ] = []  # gambiarra do momento: lista de ids de objetos para serem renderizados em outra camada
        self.scene: Scene
        self.config = config
        self.cameras = {
            "iso": IsometricCamera(),
            "fps": Camera(position=(0.0, 0.5, 2.0), pitch=-15),
        }
        self.camera_mode = "iso"  # começa na isométrica
        self.camera = self.cameras[self.camera_mode]
        self.rotate = False

    def set_camera(self, camera) -> None:
        self.camera = camera

    def update(self):
        pass

    def start(self):
        # self.scene = TestCoffe()
        self.objects.append(Chair())
        # self.objects.append(Triangle(-0.5, 0.0))
        # self.objects.append(Triangle(0.0, 0.0))
        # self.objects.append(Square(x=0.0, y=0.0))
        # self.objects.append(Block(width=0.25, height=0.75))
