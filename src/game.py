import glfw
from OpenGL.GL import *

from src.config import Config
from src.state import State


class Game:
    state: State
    config: Config

    def __init__(self):
        self.config = Config()  # Carrega as configurações padrões do jogo
        self.state = State()  # Inicia o estado da aplicação
        self.initialize_window()  # Inicializa a janela e outras configs básicas do OpenGL

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

        glClearColor(0.2, 0.3, 0.5, 0)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)

        for vaoId, vertexAmount in self.state.objectsIds:
            glBindVertexArray(vaoId)
            glDrawArrays(GL_TRIANGLES, 0, vertexAmount)

        glBindVertexArray(0)

    def run(self):
        while not glfw.window_should_close(self.state.window):
            glfw.poll_events()
            self.process_input()
            self.state.update()
            self.render()
            glfw.swap_buffers(self.state.window)

        glfw.terminate()

    def process_input(self):
        if glfw.get_key(self.state.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.state.window, True)
