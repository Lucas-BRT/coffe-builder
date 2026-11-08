from enum import Enum
from pathlib import Path

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
        self.light_position_uniform_loc = glGetUniformLocation(
            self.shader, "light_position"
        )
        self.light_color_uniform_loc = glGetUniformLocation(self.shader, "light_color")
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
        light = getattr(self.state.scene, "light", None)
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
        if light is not None:
            position = light.transform.position
            glUniform3f(
                self.light_position_uniform_loc, position.x, position.y, position.z
            )
            glUniform3f(
                self.light_color_uniform_loc,
                light.color.r,
                light.color.g,
                light.color.b,
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
        light_position = self.state.scene.light.transform.position
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
