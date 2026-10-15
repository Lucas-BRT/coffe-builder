import glfw
from pyglm import glm

from src.objects.block import Block
from src.renderer import Renderer
from src.state import State


class Controls:
    def __init__(self, state: State, renderer: Renderer):
        self.renderer = renderer
        self.state = state
        self.zoom_speed = 0.01
        self.last_x = self.last_y = None

    def use_camera(self, mode):
        self.state.camera_mode = mode
        self.state.camera = self.state.cameras[mode]
        self.last_x = self.last_y = None
        cursor = glfw.CURSOR_DISABLED if mode == "fps" else glfw.CURSOR_NORMAL
        glfw.set_input_mode(self.state.window, glfw.CURSOR, cursor)

    def set_input_handler(self):
        def key_callback(window, key, scancode, action, mods):
            if key == glfw.KEY_M and action == glfw.PRESS:
                self.renderer.togle_render_mode()
            if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
                glfw.set_window_should_close(self.state.window, True)

            if key == glfw.KEY_C and action == glfw.PRESS:
                self.use_camera("fps" if self.state.camera_mode == "iso" else "iso")

            if key == glfw.KEY_BACKSPACE and action == glfw.PRESS:
                try:
                    self.state.objects.pop()
                except:
                    pass
            if key == glfw.KEY_ENTER and action == glfw.PRESS:
                try:
                    self.state.objects.append(Block())
                except:
                    pass
            if key == glfw.KEY_R and action == glfw.PRESS:
                try:
                    self.state.rotate = not self.state.rotate
                except:
                    pass

        glfw.set_key_callback(self.state.window, key_callback)


        def mouse_callback(window, xpos, ypos):
            if self.state.camera_mode != "fps":
                return
            if self.last_x is None:  # evita o "pulo" no 1º movimento
                self.last_x, self.last_y = xpos, ypos
            dx = xpos - self.last_x
            dy = self.last_y - ypos  # invertido: y da tela cresce pra baixo
            self.last_x, self.last_y = xpos, ypos
            self.state.camera.rotate(dx, dy)

        glfw.set_cursor_pos_callback(self.state.window, mouse_callback)

        self.use_camera(self.state.camera_mode)


    def handle_dynamic_user_input(self, window, dt):
        glfw.poll_events()
        if self.state.camera_mode == "fps":
            forward = (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS) - (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS)
            strafe  = (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) - (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS)
            self.state.camera.move(forward, strafe, dt)

        speed = 0.02
        rotation_speed = speed * 3
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, x_angle=1)
            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, x_angle=-1)
            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, z_angle=1)
            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                self.state.objects[0].rotate(rotation_speed, z_angle=-1)
            if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
                self.renderer.camera.rotate(rotation_speed, y_angle=1)
            if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
                self.renderer.camera.rotate(rotation_speed, y_angle=-1)

        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            self.state.objects[0].move_at(y=speed)
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            self.state.objects[0].move_at(y=-speed)
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            self.state.objects[0].move_at(-speed)
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.state.objects[0].move_at(speed)


        if self.state.camera_mode == "iso":
            cam = self.state.camera
            if glfw.get_key(window, glfw.KEY_EQUAL) == glfw.PRESS:
                cam.set_zoom(cam.zoom_level - self.zoom_speed)
            if glfw.get_key(window, glfw.KEY_MINUS) == glfw.PRESS:
                cam.set_zoom(cam.zoom_level + self.zoom_speed)
