from __future__ import annotations

from ctypes import _Pointer

import glfw
from OpenGL.GL import glViewport

from src.config import Config


class Window:
    inner: _Pointer[glfw._GLFWwindow]
    title: str
    width: int
    height: int

    framebuffer_width: int
    framebuffer_height: int

    def __init__(self, config: Config):
        self.title = config.app_title
        self.width = config.window_width
        self.height = config.window_height

        if not glfw.init():
            glfw.terminate()
            raise RuntimeError("failed to init glfw")

        # Obriga a usar OpenGL moderno
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE) # Apenas para MacOs X

        self.inner = glfw.create_window(
            self.width,
            self.height,
            self.title,
            None,  # só se fosse colocar o jogo em fullscreen
            None,
        )

        if not self.inner:
            glfw.terminate()
            raise RuntimeError("failed to init glfw window")

        glfw.make_context_current(self.inner)

        def window_resize_callback(window, width, height):
            glViewport(0, 0, width, height)
            self.framebuffer_width, self.framebuffer_height = glfw.get_framebuffer_size(
                self.inner
            )

        glfw.set_framebuffer_size_callback(self.inner, window_resize_callback)

        self.framebuffer_width, self.framebuffer_height = glfw.get_framebuffer_size(
            self.inner
        )

    def close(self):
        glfw.set_window_should_close(self.inner, True)
