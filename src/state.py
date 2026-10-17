from __future__ import annotations

from ctypes import _Pointer

import glfw
import glm
from OpenGL.GL import *

from src.camera import Camera, IsometricCamera, PespectiveCamera
from src.config import Config
from src.objects import COLORS, Object, Transform
from src.objects.components.triangle import Triangle
from src.scenes import Scene
from src.scenes.TestCoffe import TestCoffe


class State:
    def __init__(self, config: Config) -> None:
        self.objects: list[
            Object
        ] = []  # gambiarra do momento: lista de ids de objetos para serem renderizados em outra camada
        self.scene: Scene
        self.config = config
        self.cameras = {
            "iso": IsometricCamera(),
            "fps": PespectiveCamera(position=(0.0, 0.5, 2.0), pitch=-15),
        }
        self.camera_mode = "iso"  # começa na isométrica
        self.camera = self.cameras[self.camera_mode]
        self.rotate = False
        self.selected = 0

    def set_camera(self, camera) -> None:
        self.camera = camera

    def selected_object(self):
        if not self.objects:
            return None
        return self.objects[self.selected % len(self.objects)]

    def update(self):
        pass

    def start(self):
        # self.scene = TestCoffe()
        print(f"{len(self.objects)} objetos na aplicação")

        self.objects.append(Triangle())
        self.objects.append(
            Triangle(
                transform=Transform(rotation=glm.dvec3(90, 0, 0)), color=COLORS["RED"]
            )
        )
        self.objects.append(Triangle())
        # self.objects.append(Square())
        # self.objects.append(Chair())

        # self.objects.append(Chair())
        # self.objects.append(Triangle(-0.5, 0.0))
        # self.objects.append(Triangle(0.0, 0.0))
        # self.objects.append(Square(x=0.0, y=0.0))
        # self.objects.append(Block(width=0.25, height=0.75))
        # self.objects.append(Block(color=(0.9, 0.2, 0.2)))
        # self.objects.append(
        #     Block(width=0.15, height=0.15, depth=0.15, color=(0.2, 0.4, 0.9))
        # )
