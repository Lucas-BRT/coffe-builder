from __future__ import annotations

from functools import singledispatchmethod
from math import floor
from typing import Optional, Union

import glfw
from OpenGL.GL import *

from src.cameras import CameraType
from src.cameras.isometric import IsometricCamera, IsometricRotationDirection
from src.cameras.perspective import PerspectiveCamera
from src.config import Config
from src.events import (
    ChangeCameraRequest,
    CloseApplication,
    Event,
    MoveCamera,
    MoveSelectedObject,
    RemoveLastObject,
    RotateCamera,
    RotateIsometricCamera,
    SelectNextObject,
    SpawObject,
    UpdateZoomLevel,
)
from src.objects import COLORS, Entity, Transform
from src.objects.components import Block
from src.objects.cursor import CURSOR_GRID_STEP, Cursor
from src.scenes import Scene
from src.scenes.coffee_shop import CoffeeShopScene
from src.window import Window

AnyCamera = Union[IsometricCamera, PerspectiveCamera]


class State:
    def __init__(self, config: Config, window: Window) -> None:
        self.window: Window = window
        self.scene: Scene
        self.config = config
        self.isometric_camera = IsometricCamera()
        self.perspective_camera = PerspectiveCamera()
        self.camera: AnyCamera = self.isometric_camera  # começa na isométrica
        self.cursor = Cursor()
        self.world_grid = Block(
            transform=Transform.at(0, -0.0575, 0),
            color=COLORS["WHITE"],
            grid_enabled=True,
            self_shadow_enabled=False,
        )
        self.selected = 0

    @property
    def camera_mode(self) -> CameraType:
        return self.camera.type

    def camera_for(self, camera_type: CameraType) -> AnyCamera:
        if camera_type is CameraType.Isometric:
            return self.isometric_camera
        if camera_type is CameraType.Perspective:
            return self.perspective_camera
        raise ValueError(f"camera sem instância no State: {camera_type}")

    def selected_object(self) -> Optional[Entity]:
        objects = self.scene.objects
        if not objects:
            return None
        return objects[self.selected % len(objects)]

    def update_cursor(self, x: float, y: float) -> None:
        window = self.window
        world = self.isometric_camera.mouse_to_world(
            x,
            y,
            window.width,
            window.height,
            window.framebuffer_width / max(window.framebuffer_height, 1),
        )
        x = (floor(world.x / CURSOR_GRID_STEP) + 0.5) * CURSOR_GRID_STEP
        z = (floor(world.z / CURSOR_GRID_STEP) + 0.5) * CURSOR_GRID_STEP
        self.cursor.move_to(x, 0, z)

    def update_world_grid(self, aspect: float) -> None:
        window = self.window
        center = self.isometric_camera.mouse_to_world(
            window.width / 2,
            window.height / 2,
            window.width,
            window.height,
            aspect,
        )
        size = max(
            self.isometric_camera.zoom_level,
            self.isometric_camera.zoom_level * aspect,
        ) * 8
        self.world_grid.move_to(center.x, -0.0575, center.z)
        self.world_grid.scale_to(size, 0.005, size)

    def update(self, dt: float = 0.0) -> None:
        self.isometric_camera.update_rotation(dt)
        if self.camera_mode is CameraType.Isometric:
            x, y = glfw.get_cursor_pos(self.window.inner)
            self.update_cursor(x, y)

    @singledispatchmethod
    def handle_event(
        self,
        event: Event,
    ) -> None:

        print("event not handled: ", event)

    @handle_event.register
    def _(self, event: CloseApplication) -> None:
        self.window.close()

    @handle_event.register
    def _(self, event: SpawObject) -> None:
        self.scene.objects.append(event.object)
        print(f"spawed object {event.object}")

    @handle_event.register
    def _(self, event: RemoveLastObject) -> None:
        if self.scene.objects:
            object = self.scene.objects.pop()
            print(f"removed object: {object}")

    @handle_event.register
    def _(self, event: SelectNextObject) -> None:
        if self.scene.objects:
            self.selected = (self.selected + 1) % len(self.scene.objects)

    @handle_event.register
    def _(self, event: MoveSelectedObject) -> None:
        obj = self.selected_object()
        if obj is not None:
            obj.move_by(event.dx, event.dy, event.dz)

    @handle_event.register
    def _(self, event: ChangeCameraRequest) -> None:

        # rotaciona para o próximo tipo de camera disponível
        self.camera = self.camera_for(self.camera_mode.next())
        print(f"change camera type to: {self.camera.type}")
        cursor_type = (
            glfw.CURSOR_DISABLED
            if isinstance(self.camera, PerspectiveCamera)
            else glfw.CURSOR_NORMAL
        )
        glfw.set_input_mode(self.window.inner, glfw.CURSOR, cursor_type)

    @handle_event.register
    def _(self, event: MoveCamera) -> None:
        # as duas câmeras andam com WASD, cada uma do seu jeito
        self.camera.move(event.forward, event.strafe, event.dt)

    @handle_event.register
    def _(self, event: RotateCamera) -> None:
        camera = self.camera
        if isinstance(camera, PerspectiveCamera):
            camera.rotate(event.dx, event.dy)

    @handle_event.register
    def _(self, event: RotateIsometricCamera) -> None:
        direction = 1 if event.direction is IsometricRotationDirection.Left else -1
        self.isometric_camera.rotate_quarter_turn(direction)

    @handle_event.register
    def _(self, event: UpdateZoomLevel) -> None:
        camera = self.camera
        if isinstance(camera, IsometricCamera):
            camera.set_zoom(camera.zoom_level + event.amount)

    def start(self) -> None:
        self.scene = CoffeeShopScene()
        self.isometric_camera.set_zoom(self.scene.iso_zoom)
        print(f"{len(self.scene.objects)} objetos na aplicação")
