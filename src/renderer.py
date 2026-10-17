from enum import Enum
from pathlib import Path

import glfw
from OpenGL.GL import *
from pyglm import glm

from src.state import State

SHADERS_DIR = Path(__file__).resolve().parent.parent / "shaders"


class RenderMode(Enum):
    NORMAL = GL_FILL
    WIREFRAME = GL_LINE


class Renderer:
    def __init__(self):
        self.render_mode = RenderMode.NORMAL
        self.shader = Renderer.create_program(
            self.read_shader("main.vert"), self.read_shader("main.frag")
        )
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")
        self.proj_loc = glGetUniformLocation(self.shader, "projection")
        self.color_loc = glGetUniformLocation(self.shader, "color")
        glEnable(GL_DEPTH_TEST)

    def render(self, state: State):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

        w, h = glfw.get_framebuffer_size(state.window)
        cam = state.camera
        view = cam.view_matrix()
        proj = cam.projection_matrix(w / max(h, 1))
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, glm.value_ptr(proj))

        for obj in state.objects:
            obj.render(self)

        glBindVertexArray(0)

    def togle_render_mode(self):
        if self.render_mode == RenderMode.NORMAL:
            self.render_mode = RenderMode.WIREFRAME
        else:
            self.render_mode = RenderMode.NORMAL

    @staticmethod
    def read_shader(file_name):
        return (SHADERS_DIR / file_name).read_text()

    @staticmethod
    def compile_shader(tipo, src):
        shader = glCreateShader(tipo)
        glShaderSource(shader, src)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise RuntimeError(f"{tipo}: {glGetShaderInfoLog(shader).decode()}")
        return shader

    @staticmethod
    def create_program(vertex_src, fragment_src):
        vs = Renderer.compile_shader(GL_VERTEX_SHADER, vertex_src)
        fs = Renderer.compile_shader(GL_FRAGMENT_SHADER, fragment_src)

        program = glCreateProgram()
        glAttachShader(program, vs)
        glAttachShader(program, fs)
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(program))

        glDeleteShader(vs)
        glDeleteShader(fs)
        return program
