import glfw
from OpenGL.GL import *

from src.config import Config
from src.controls import Controls
from src.renderer import Renderer
from src.state import State
from src.window import Window


class Game:
    def __init__(self):
        self.config = Config()  # Carrega as configurações padrões do jogo
        self.window = Window(self.config)  # Inicia a janela e configs do OpenGL
        self.state = State(self.config, self.window)  # Inicia o estado da aplicação
        self.renderer = Renderer()
        self.controls = Controls(self.state, self.renderer)
        self.state.start()

    def run(self) -> None:
        self.controls.set_input_handler()
        last = glfw.get_time()
        while not glfw.window_should_close(self.state.window.inner):
            now = glfw.get_time()
            dt, last = now - last, now
            self.controls.handle_dynamic_user_input(self.state.window, dt)
            self.state.update()
            self.renderer.render(self.state)
            glfw.swap_buffers(self.state.window.inner)

        glfw.terminate()
