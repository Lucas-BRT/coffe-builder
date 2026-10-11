import glfw

from src.renderer import Renderer
from src.state import State


class Controls:
    def __init__(self, state: State, renderer: Renderer):
        self.renderer = renderer
        self.state = state

    def set_input_handler(self):
        def key_callback(window, key, scancode, action, mods):
            if key == glfw.KEY_M and action == glfw.PRESS:
                self.renderer.togle_render_mode()
            if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
                glfw.set_window_should_close(self.state.window, True)
            # if key == glfw.KEY_RIGHT and action == glfw.PRESS:
            #     self.state.objects[0].translate(y=0.01)

        glfw.set_key_callback(self.state.window, key_callback)

    def handle_dynamic_user_input(self, window):
        glfw.poll_events()
        speed = 0.01
        rotation_speed = speed * 3

        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            self.state.objects[0].move_at(y=speed)
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            self.state.objects[0].move_at(y=-speed)
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            self.state.objects[0].rotate(rotation_speed, z_angle=1)
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.state.objects[0].rotate(-rotation_speed, z_angle=1)
