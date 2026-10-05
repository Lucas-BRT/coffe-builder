from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import *


class State:
    window: _Pointer[
        glfw._GLFWwindow
    ]  # precisa do __future__ annotations para deixar selecionar o tipo sem dar pau na 3.8
    objectsIds = []  # gambiarra do momento: lista de ids de objetos para serem renderizados em outra camada

    def __init__(self) -> None:
        pass

    def update(self):
        pass
