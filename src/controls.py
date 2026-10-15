import glfw

from src.objects.block import Block
from src.renderer import Renderer
from src.state import State


class Controls:
    def __init__(self, state: State, renderer: Renderer):
        self.renderer = renderer
        self.state = state

    def set_input_handler(self):
        glfw.set_input_mode(self.state.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        self.last_x = self.last_y = None

        def mouse_callback(window, xpos, ypos):
            if self.last_x is None:                  # evita o "pulo" no 1º movimento
                self.last_x, self.last_y = xpos, ypos
            dx = xpos - self.last_x
            dy = self.last_y - ypos                  # invertido: y da tela cresce pra baixo
            self.last_x, self.last_y = xpos, ypos
            self.state.camera.rotate(dx, dy)

        glfw.set_cursor_pos_callback(self.state.window, mouse_callback)


    def handle_dynamic_user_input(self, window, dt):
        glfw.poll_events()
        forward = (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS) - (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS)
        strafe  = (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) - (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS)
        self.state.camera.move(forward, strafe, dt)

        speed = 0.01
        rotation_speed = speed * 3
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, x_angle=1)
            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, x_angle=-1)
            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, y_angle=1)
            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, y_angle=-1)
        else:
            if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                self.state.objects[0].move_at(y=speed)
            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                self.state.objects[0].move_at(y=-speed)
            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                self.state.objects[0].move_at(-speed)
            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                self.state.objects[0].move_at(speed)
