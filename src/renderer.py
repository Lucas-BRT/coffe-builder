from enum import Enum
from pathlib import Path

from OpenGL.GL import *
from pyglm import glm

SHADERS_DIR = Path(__file__).resolve().parent.parent / "shaders"


class RenderMode(Enum):
    NORMAL = GL_FILL
    WIREFRAME = GL_LINE


class Renderer:
    def __init__(self, state):
        self.state = state
        self.shader = Renderer.create_program(
            self.read_shader("main.vert"), self.read_shader("main.frag")
        )
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.render_mode = RenderMode.NORMAL

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)

        for obj in self.state.objects:
            glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, glm.value_ptr(obj.model))
            glBindVertexArray(obj.vao)
            glPolygonMode(GL_FRONT_AND_BACK, self.render_mode.value)
            glDrawArrays(GL_TRIANGLES, 0, obj.vertex_count)

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
