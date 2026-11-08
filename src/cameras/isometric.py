from __future__ import annotations

from enum import Enum, auto
from typing import Tuple, cast

from pyglm import glm

from src.cameras import Camera, CameraType


class IsometricRotationDirection(Enum):
    Right = auto()
    Left = auto()


class IsometricCamera(Camera):
    type: CameraType = CameraType.Isometric
    speed = 1.0  # metade da tela por SEGUNDO (com zoom 1)

    def __init__(
        self,
        x_pos: float = 1,
        y_pos: float = 1,
        z_pos: float = 1,
        zoom_level: float = 1,
        lokin_at_x: float = 1,
        lokin_at_y: float = 1,
        lokin_at_z: float = 1,
        aspect_ratio: float = 1,
    ) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos

        self.zoom_level = zoom_level

        self.lokin_at_x = lokin_at_x
        self.lokin_at_y = lokin_at_y
        self.lokin_at_z = lokin_at_z

        self.aspect_ratio = aspect_ratio
        self._rotation_queue: list[int] = []
        self._rotation_direction = 0
        self._rotation_elapsed = 0.0
        self._rotation_previous_progress = 0.0

        # câmera na diagonal (1,1,1) olhando para a origem
        self.view: glm.mat4x4 = glm.lookAt(
            glm.vec3(1.0, 1.0, 1.0),  # posição
            glm.vec3(0.0, 0.0, 0.0),  # alvo
            glm.vec3(0.0, 1.0, 0.0),  # up
        )

    def view_matrix(self) -> glm.mat4x4:
        return self.view

    def projection_matrix(self, aspect: float) -> glm.mat4x4:
        z = self.zoom_level
        # near negativo e grande: na ortográfica não tem problema enxergar
        # "atrás" da câmera, e assim cenas grandes não ficam cortadas
        return glm.ortho(-z * aspect, z * aspect, -z, z, -100.0, 100.0)

    def mouse_ray(
        self, x: float, y: float, window_width: int, window_height: int, aspect: float
    ) -> Tuple[glm.vec3, glm.vec3]:
        """Raio (origem, direção) que sai da câmera passando pelo cursor"""
        ndc_x = 2.0 * x / window_width - 1.0
        ndc_y = 1.0 - 2.0 * y / window_height
        inverse_view_projection = glm.inverse(self.projection_matrix(aspect) * self.view)
        near = inverse_view_projection * glm.vec4(ndc_x, ndc_y, -1.0, 1.0)
        far = inverse_view_projection * glm.vec4(ndc_x, ndc_y, 1.0, 1.0)
        near = glm.vec3(near) / near.w
        far = glm.vec3(far) / far.w
        return near, far - near

    def mouse_to_world(
        self,
        x: float,
        y: float,
        window_width: int,
        window_height: int,
        aspect: float,
        plane_y: float = 0.0,
    ) -> glm.vec3:
        """Converte a posição GLFW do cursor no ponto do plano horizontal."""
        near, direction = self.mouse_ray(x, y, window_width, window_height, aspect)

        if abs(direction.y) < 1e-8:
            raise ValueError("raio do mouse paralelo ao plano")

        distance = (plane_y - near.y) / direction.y
        return near + distance * direction

    def move(self, forward: int, strafe: int, dt: float) -> None:
        """
        Anda pelo mapa relativo à tela: W/S sobem/descem, A/D vão para os lados.

        Desliza no plano da tela em vez do chão: como a projeção é ortográfica,
        a imagem fica igual, mas a distância até os objetos não muda, então
        eles não somem por sair do near/far depois de andar muito.
        """
        direction = glm.vec3(strafe, forward, 0.0)
        if glm.length(direction) > 0:
            # com zoom afastado o mapa parece menor, então anda mais rápido
            step = glm.normalize(direction) * self.speed * self.zoom_level * dt
            # mover a câmera para um lado = mover o mundo para o outro.
            # o cast é só pro linter parar de confundir uma mat4x2 com mat4x4
            # não altera o valor
            self.view = cast(glm.mat4x4, glm.translate(-step) * self.view)

    def move_at(
        self, x_pos: float = 0.0, y_pos: float = 0.0, z_pos: float = 0.0
    ) -> None:
        self.translate(x_pos, y_pos, z_pos)

    def translate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.view = glm.translate(self.view, glm.vec3(x, y, z))

    def rotate(
        self,
        angle: float = 0.0,
        x_angle: float = 0.0,
        y_angle: float = 0.0,
        z_angle: float = 0.0,
    ) -> None:
        # mesmo que self.view * glm.rotate(angle, eixo), mas tipado certo nos stubs
        self.view = glm.rotate(self.view, angle, glm.vec3(x_angle, y_angle, z_angle))

    def rotate_quarter_turn(self, direction: int) -> None:
        self._rotation_queue.append(direction)

    def update_rotation(self, dt: float) -> None:
        if not self._rotation_direction and self._rotation_queue:
            self._rotation_direction = self._rotation_queue.pop(0)
            self._rotation_elapsed = 0.0
            self._rotation_previous_progress = 0.0
        if not self._rotation_direction:
            return

        duration = 0.25
        self._rotation_elapsed = min(self._rotation_elapsed + dt, duration)
        progress = self._rotation_elapsed / duration
        eased = progress * progress * (3.0 - 2.0 * progress)
        angle = glm.radians(90.0) * (eased - self._rotation_previous_progress)
        self.rotate(angle, y_angle=self._rotation_direction)
        self._rotation_previous_progress = eased

        if progress == 1.0:
            self._rotation_direction = 0

    def set_zoom(self, zoom: float = 1) -> None:
        self.zoom_level = max(0.05, zoom)  # zoom <= 0 inverteria a imagem
