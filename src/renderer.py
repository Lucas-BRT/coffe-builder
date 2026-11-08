from enum import Enum
from pathlib import Path

import numpy as np
from OpenGL.GL import *
from pyglm import glm

from src.cameras import CameraType
from src.objects import COLORS
from src.sidebar import Sidebar
from src.state import State

SHADERS_DIR = Path(__file__).resolve().parent.parent / "shaders"


class RenderMode(Enum):
    NORMAL = GL_FILL
    WIREFRAME = GL_LINE


class Renderer:
    shadow_size = 512
    shadow_far_plane = 100.0

    def __init__(self, state: State):
        self.render_mode = RenderMode.NORMAL
        self.shader = Renderer.create_program(
            self.read_shader("main.vert"), self.read_shader("main.frag")
        )
        self.model_uniform_loc = glGetUniformLocation(self.shader, "model")
        self.view_uniform_loc = glGetUniformLocation(self.shader, "view")
        self.proj_uniform_loc = glGetUniformLocation(self.shader, "projection")
        self.color_uniform_loc = glGetUniformLocation(self.shader, "color")
        self.grid_uniform_loc = glGetUniformLocation(self.shader, "grid_enabled")
        self.emissive_uniform_loc = glGetUniformLocation(self.shader, "emissive")
        self.self_shadow_uniform_loc = glGetUniformLocation(
            self.shader, "self_shadow_enabled"
        )
        self.light_count_uniform_loc = glGetUniformLocation(self.shader, "light_count")
        self.shadow_light_uniform_loc = glGetUniformLocation(
            self.shader, "shadow_light"
        )
        self.light_positions_uniform_loc = glGetUniformLocation(
            self.shader, "light_positions"
        )
        self.light_colors_uniform_loc = glGetUniformLocation(
            self.shader, "light_colors"
        )
        self.light_falloff_uniform_loc = glGetUniformLocation(
            self.shader, "light_falloff"
        )
        self.lights: list = []
        self.camera_position_uniform_loc = glGetUniformLocation(
            self.shader, "camera_position"
        )
        self.shadow_map_uniform_loc = glGetUniformLocation(self.shader, "shadow_map")
        self.shadow_far_uniform_loc = glGetUniformLocation(
            self.shader, "shadow_far_plane"
        )
        self.shadow_shader = Renderer.create_program(
            self.read_shader("shadow.vert"), self.read_shader("shadow.frag")
        )
        self.shadow_model_uniform_loc = glGetUniformLocation(
            self.shadow_shader, "model"
        )
        self.shadow_matrix_uniform_loc = glGetUniformLocation(
            self.shadow_shader, "light_space_matrix"
        )
        self.shadow_light_position_uniform_loc = glGetUniformLocation(
            self.shadow_shader, "light_position"
        )
        self.shadow_far_plane_uniform_loc = glGetUniformLocation(
            self.shadow_shader, "shadow_far_plane"
        )
        self.texture_uniform_loc = glGetUniformLocation(self.shader, "tex")
        self.use_texture_uniform_loc = glGetUniformLocation(self.shader, "useTexture")
        self.grid_visible = False
        self.state = state
        self.sidebar = Sidebar()

        self.shadow_fbo = int(glGenFramebuffers(1))
        self.shadow_map = int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.shadow_map)
        for face in range(6):
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                0,
                GL_DEPTH_COMPONENT24,
                self.shadow_size,
                self.shadow_size,
                0,
                GL_DEPTH_COMPONENT,
                GL_FLOAT,
                None,
            )
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

        glPolygonMode(GL_FRONT_AND_BACK, self.render_mode.value)
        glClearColor(*COLORS["WHITE"].to_gpu())
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def render(self) -> None:
        cam = self.state.camera
        view = cam.view_matrix()
        proj = cam.projection_matrix(
            # Tecnicamente o GLFW não permite uma janela com 0 de
            # altura por padrão mas é bom deixar o max(height, 1)
            # por segurança mesmo
            self.state.window.framebuffer_width
            / max(self.state.window.framebuffer_height, 1)
        )
        self.grid_visible = self.state.camera_mode is CameraType.Isometric
        glClear(GL_DEPTH_BUFFER_BIT)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)
        glUniformMatrix4fv(self.view_uniform_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(self.proj_uniform_loc, 1, GL_FALSE, glm.value_ptr(proj))
        camera_position = glm.vec3(glm.inverse(view) * glm.vec4(0, 0, 0, 1))
        glUniform3f(
            self.camera_position_uniform_loc,
            camera_position.x,
            camera_position.y,
            camera_position.z,
        )
        glUniform1i(self.texture_uniform_loc, 1)
        glUniform1i(self.shadow_map_uniform_loc, 0)
        glUniform1f(self.shadow_far_uniform_loc, self.shadow_far_plane)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.shadow_map)
        self.lights = self.state.scene.light_sources()
        glUniform1i(self.light_count_uniform_loc, len(self.lights))
        if self.lights:
            glUniform3fv(
                self.light_positions_uniform_loc,
                len(self.lights),
                np.array([p.to_tuple() for p, _, _ in self.lights], dtype=np.float32),
            )
            glUniform3fv(
                self.light_colors_uniform_loc,
                len(self.lights),
                np.array([(c.r, c.g, c.b) for _, c, _ in self.lights], dtype=np.float32),
            )
            glUniform1fv(
                self.light_falloff_uniform_loc,
                len(self.lights),
                np.array([f for _, _, f in self.lights], dtype=np.float32),
            )
        if self.grid_visible:
            self.state.update_world_grid(
                self.state.window.framebuffer_width
                / max(self.state.window.framebuffer_height, 1)
            )
            self.state.world_grid.render(self)

        # Renderiza a cena que está carregada atualmente no estado
        # usando o renderizador atual
        self.state.scene.render(self)
        if self.state.camera_mode is CameraType.Isometric:
            for box in self.state.highlights():
                box.render(self)
            self.state.cursor.render(self)
            self.sidebar.render(
                self.state.window.width,
                self.state.window.height,
                self.render_mode.value,
            )

        glBindVertexArray(0)

    def render_self_shadow(self, entity) -> None:
        directions = (
            (glm.vec3(1, 0, 0), glm.vec3(0, -1, 0)),
            (glm.vec3(-1, 0, 0), glm.vec3(0, -1, 0)),
            (glm.vec3(0, 1, 0), glm.vec3(0, 0, 1)),
            (glm.vec3(0, -1, 0), glm.vec3(0, 0, -1)),
            (glm.vec3(0, 0, 1), glm.vec3(0, -1, 0)),
            (glm.vec3(0, 0, -1), glm.vec3(0, -1, 0)),
        )
        # a sombra própria vem da lâmpada mais próxima do objeto. Sol e lua ficam
        # de fora: de tão longe o mapa de sombra fica sem resolução e dá acne
        lamps = [i for i, (_, _, falloff) in enumerate(self.lights) if falloff > 0]
        if not lamps:
            glUniform1i(self.shadow_light_uniform_loc, -1)
            return
        low, high = entity.bounds()
        center = (low + high) / 2
        shadow_light = min(
            lamps, key=lambda i: glm.distance(self.lights[i][0], center)
        )
        light_position = self.lights[shadow_light][0]
        projection = glm.perspective(
            glm.radians(90.0), 1.0, 0.1, self.shadow_far_plane
        )
        glUseProgram(self.shadow_shader)
        glUniform3f(
            self.shadow_light_position_uniform_loc,
            light_position.x,
            light_position.y,
            light_position.z,
        )
        glUniform1f(self.shadow_far_plane_uniform_loc, self.shadow_far_plane)
        glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_fbo)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glViewport(0, 0, self.shadow_size, self.shadow_size)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        for face, (direction, up) in enumerate(directions):
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_DEPTH_ATTACHMENT,
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                self.shadow_map,
                0,
            )
            if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
                raise RuntimeError("self-shadow framebuffer is incomplete")
            light_view = glm.lookAt(light_position, light_position + direction, up)
            light_space = projection * light_view
            glUniformMatrix4fv(
                self.shadow_matrix_uniform_loc, 1, GL_FALSE, glm.value_ptr(light_space)
            )
            glClear(GL_DEPTH_BUFFER_BIT)
            entity.render_shadow(self)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(
            0,
            0,
            self.state.window.framebuffer_width,
            self.state.window.framebuffer_height,
        )
        glPolygonMode(GL_FRONT_AND_BACK, self.render_mode.value)
        glUseProgram(self.shader)
        glUniform1i(self.shadow_light_uniform_loc, shadow_light)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.shadow_map)

    def togle_render_mode(self):
        if self.render_mode is RenderMode.NORMAL:
            self.render_mode = RenderMode.WIREFRAME
        elif self.render_mode is RenderMode.WIREFRAME:
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
