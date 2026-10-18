from __future__ import annotations

from functools import singledispatchmethod
from typing import Optional, Union

import glfw
from OpenGL.GL import *

from src.camera import (
    CameraType,
    IsometricCamera,
    IsometricRotationDirection,
    PerspectiveCamera,
)
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
from src.objects import Object
from src.scenes import Scene
from src.scenes.debug import DebugScene
from src.window import Window

AnyCamera = Union[IsometricCamera, PerspectiveCamera]


class State:
    def __init__(self, config: Config, window: Window) -> None:
        self.window: Window = window
        self.scene: Scene
        self.config = config
        self.isometric_camera = IsometricCamera()
        self.perspective_camera = PerspectiveCamera(position=(0.0, 0.5, 2.0), pitch=-15)
        self.camera: AnyCamera = self.isometric_camera  # começa na isométrica
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

    def selected_object(self) -> Optional[Object]:
        objects = self.scene.objects
        if not objects:
            return None
        return objects[self.selected % len(objects)]

    def update(self) -> None:
        pass

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

    @handle_event.register
    def _(self, event: RemoveLastObject) -> None:
        if self.scene.objects:
            self.scene.objects.pop()

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
        camera = self.isometric_camera
        y_angle = 1 if event.direction is IsometricRotationDirection.Left else -1
        camera.rotate(camera.rotation_speed, y_angle=y_angle)

    @handle_event.register
    def _(self, event: UpdateZoomLevel) -> None:
        camera = self.camera
        if isinstance(camera, IsometricCamera):
            camera.set_zoom(camera.zoom_level + event.amount)

    def start(self) -> None:
        self.scene = DebugScene()
        print(f"{len(self.scene.objects)} objetos na aplicação")
