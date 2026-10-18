from typing import Optional

import glfw

from src.camera import CameraType, IsometricRotationDirection
from src.events import (
    ChangeCameraRequest,
    CloseApplication,
    MoveCamera,
    MoveSelectedObject,
    RemoveLastObject,
    RotateCamera,
    RotateIsometricCamera,
    SelectNextObject,
    SpawObject,
    UpdateZoomLevel,
)
from src.objects.components.shapes2d.square import Square
from src.renderer import Renderer
from src.state import State
from src.window import Window


class Controls:
    def __init__(self, state: State, renderer: Renderer) -> None:
        self.renderer = renderer
        self.state = state
        self.zoom_speed = 0.01
        self.move_speed = 0.02
        self.last_x: Optional[float] = None
        self.last_y: Optional[float] = None

    def set_input_handler(self) -> None:
        def key_callback(window, key: int, scancode: int, action: int, mods: int) -> None:
            if action != glfw.PRESS:
                return

            if key == glfw.KEY_M:
                self.renderer.togle_render_mode()
            if key == glfw.KEY_ESCAPE:
                self.state.handle_event(CloseApplication())
            if key == glfw.KEY_C:
                self.state.handle_event(ChangeCameraRequest())
                self.last_x = self.last_y = None
            if key == glfw.KEY_TAB:
                self.state.handle_event(SelectNextObject())
            if key == glfw.KEY_BACKSPACE:
                self.state.handle_event(RemoveLastObject())
            if key == glfw.KEY_ENTER:
                self.state.handle_event(SpawObject(object=Square()))

        glfw.set_key_callback(self.state.window.inner, key_callback)

        def mouse_callback(window, xpos: float, ypos: float) -> None:
            if self.state.camera_mode != CameraType.Perspective:
                return
            if self.last_x is None or self.last_y is None:
                # 1º movimento só marca a posição, evita o "pulo" da câmera
                self.last_x, self.last_y = xpos, ypos
                return
            dx = xpos - self.last_x
            dy = self.last_y - ypos  # invertido: y da tela cresce pra baixo
            self.last_x, self.last_y = xpos, ypos
            self.state.handle_event(RotateCamera(dx=dx, dy=dy))

        glfw.set_cursor_pos_callback(self.state.window.inner, mouse_callback)

    def handle_dynamic_user_input(self, window: Window, dt: float) -> None:
        glfw.poll_events()

        def pressed(key: int) -> bool:
            return glfw.get_key(window.inner, key) == glfw.PRESS

        forward = pressed(glfw.KEY_W) - pressed(glfw.KEY_S)
        strafe = pressed(glfw.KEY_D) - pressed(glfw.KEY_A)
        if forward or strafe:
            self.state.handle_event(MoveCamera(forward=forward, strafe=strafe, dt=dt))

        if pressed(glfw.KEY_LEFT_SHIFT):
            if pressed(glfw.KEY_Q):
                self.state.handle_event(
                    RotateIsometricCamera(direction=IsometricRotationDirection.Left)
                )
            if pressed(glfw.KEY_E):
                self.state.handle_event(
                    RotateIsometricCamera(direction=IsometricRotationDirection.Right)
                )

        dx = (pressed(glfw.KEY_RIGHT) - pressed(glfw.KEY_LEFT)) * self.move_speed
        dy = (pressed(glfw.KEY_UP) - pressed(glfw.KEY_DOWN)) * self.move_speed
        if dx or dy:
            self.state.handle_event(MoveSelectedObject(dx=dx, dy=dy))

        if pressed(glfw.KEY_EQUAL):
            self.state.handle_event(UpdateZoomLevel(amount=-self.zoom_speed))
        if pressed(glfw.KEY_MINUS):
            self.state.handle_event(UpdateZoomLevel(amount=self.zoom_speed))
