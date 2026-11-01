from typing import Optional

import glfw

from src.cameras import CameraType
from src.cameras.isometric import IsometricRotationDirection
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


class Controls:
    def __init__(self, state: State, renderer: Renderer) -> None:
        self.renderer = renderer
        self.state = state
        self.zoom_speed = 0.10
        self.move_speed = 0.02
        self.last_x: Optional[float] = None
        self.last_y: Optional[float] = None

    def pressed(self, key: int) -> bool:
        return glfw.get_key(self.state.window.inner, key) == glfw.PRESS

    def set_input_handler(self) -> None:
        def key_callback(
            window, key: int, scancode: int, action: int, mods: int
        ) -> None:
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

        def scroll_callback(window, xoffset, yoffset):

            # como o teclado está lendo no modo de leitura de "escuta"
            # e o mouse está lendo no modo de callback, mouses sem rodas livres
            # tendem a mandar menos comandos sequenciais, fazendo o zoom
            # parecer mais lento no scroll do mouse.
            #
            # essa variávle calibra isso
            mouse_zoom_tick_bonus = 2
            if yoffset > 0:
                self.state.handle_event(
                    UpdateZoomLevel(amount=-self.zoom_speed * mouse_zoom_tick_bonus)
                )
            else:
                self.state.handle_event(
                    UpdateZoomLevel(amount=self.zoom_speed * mouse_zoom_tick_bonus)
                )

        def mouse_callback(window, xpos: float, ypos: float) -> None:
            if self.state.camera_mode == CameraType.Perspective:
                if self.last_x is None or self.last_y is None:
                    # 1º movimento só marca a posição, evita o "pulo" da câmera
                    self.last_x, self.last_y = xpos, ypos
                    return
                dx = xpos - self.last_x
                dy = self.last_y - ypos  # invertido: y da tela cresce pra baixo
                self.last_x, self.last_y = xpos, ypos
                self.state.handle_event(RotateCamera(dx=dx, dy=dy))
            if self.state.camera_mode == CameraType.Isometric:
                # TODO: implementar os outros comandos da camera isometrica
                pass

        glfw.set_key_callback(self.state.window.inner, key_callback)
        glfw.set_cursor_pos_callback(self.state.window.inner, mouse_callback)
        glfw.set_scroll_callback(self.state.window.inner, scroll_callback)

    def handle_dynamic_user_input(self, dt: float) -> None:
        glfw.poll_events()

        self.handle_player_move(dt)
        self.handle_window_resize()
        self.handle_isometric_camera_rotation()
        self.handle_isometric_camera_zoom()
        self.handle_object_manual_move()

    def handle_object_manual_move(self):

        dx = (
            self.pressed(glfw.KEY_RIGHT) - self.pressed(glfw.KEY_LEFT)
        ) * self.move_speed
        dy = (self.pressed(glfw.KEY_UP) - self.pressed(glfw.KEY_DOWN)) * self.move_speed
        if dx or dy:
            self.state.handle_event(MoveSelectedObject(dx=dx, dy=dy))

    def handle_isometric_camera_zoom(self):
        if self.pressed(glfw.KEY_EQUAL):
            self.state.handle_event(UpdateZoomLevel(amount=-self.zoom_speed))
        if self.pressed(glfw.KEY_MINUS):
            self.state.handle_event(UpdateZoomLevel(amount=self.zoom_speed))

    def handle_isometric_camera_rotation(self):
        if self.pressed(glfw.KEY_LEFT_SHIFT):
            if self.pressed(glfw.KEY_Q):
                self.state.handle_event(
                    RotateIsometricCamera(direction=IsometricRotationDirection.Left)
                )
            if self.pressed(glfw.KEY_E):
                self.state.handle_event(
                    RotateIsometricCamera(direction=IsometricRotationDirection.Right)
                )

    def handle_player_move(self, dt: float = 0):
        forward = self.pressed(glfw.KEY_W) - self.pressed(glfw.KEY_S)
        strafe = self.pressed(glfw.KEY_D) - self.pressed(glfw.KEY_A)
        if forward or strafe:
            self.state.handle_event(MoveCamera(forward=forward, strafe=strafe, dt=dt))

    def handle_window_resize(self):
        self.state.window.width, self.state.window.height = glfw.get_window_size(
            self.state.window.inner
        )
