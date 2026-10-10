import glfw
from OpenGL.GL import *

from src.config import Config
from src.controls import Controls
from src.renderer import Renderer
from src.state import State


class Game:
    def __init__(self):
        self.config = Config()  # Carrega as configurações padrões do jogo
        self.state = State()  # Inicia o estado da aplicação
        self.initialize_window()  # Inicializa a janela e outras configs básicas do OpenGL
        self.renderer = Renderer(self.state)
        self.controls = Controls(self.state, self.renderer)
        self.state.load_objects()

    def initialize_window(self):
        if not glfw.init():
            glfw.terminate()
            raise RuntimeError("failed to init glfw")

        # Obriga a usar OpenGL moderno
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE) # Apenas para MacOs X

        self.state.window = glfw.create_window(
            self.config.window_width,
            self.config.window_height,
            self.config.app_title,
            None,  # só se fosse colocar o jogo em fullscreen
            None,
        )

        if not self.state.window:
            glfw.terminate()
            raise RuntimeError("failed to init glfw window")

        glfw.make_context_current(self.state.window)

        def window_resize_callback(window, width, height):
            glViewport(0, 0, width, height)

        glfw.set_framebuffer_size_callback(self.state.window, window_resize_callback)

    def run(self):
        self.controls.set_input_handler()

        while not glfw.window_should_close(self.state.window):
            self.controls.handle_dynamic_user_input(self.state.window)
            self.state.update()
            self.renderer.render()
            glfw.swap_buffers(self.state.window)

        glfw.terminate()
