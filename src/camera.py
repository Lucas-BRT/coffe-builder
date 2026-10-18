from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, cast

from pyglm import glm


class CameraType(Enum):
    Isometric = auto()
    Perspective = auto()

    def next(self) -> CameraType:
        """
        Apenas um helper para "rotacionar" entre os tipos de cameras,
        se for preciso adicionar outros tipos no futuro, o método next
        vai garantir que rotacionemos entre elas sem precisar de teclas
        extras
        """
        types = list(CameraType)
        return types[(types.index(self) + 1) % len(types)]


@dataclass
class Camera:
    position: glm.vec3 = field(default_factory=glm.vec3)

    @abstractmethod
    def view_matrix(self) -> glm.mat4x4:
        pass

    @abstractmethod
    def projection_matrix(self, aspect: float) -> glm.mat4x4:
        pass


class PerspectiveCamera:
    type: CameraType = CameraType.Perspective

    def __init__(
        self,
        position: Tuple[float, float, float] = (0.0, 0.2, 0.2),
        yaw: float = -90,
        pitch: float = 0.0,
    ) -> None:
        self.position = glm.vec3(*position)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 0.4  # unidades por SEGUNDO
        self.sensitivity = 0.1
        self.fov = 70.0
        self._update_vectors()

    def _update_vectors(self) -> None:
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
        self.front = glm.normalize(
            glm.vec3(
                glm.cos(yaw) * glm.cos(pitch),
                glm.sin(pitch),
                glm.sin(yaw) * glm.cos(pitch),
            )
        )
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.cross(self.right, self.front)

    def view_matrix(self) -> glm.mat4x4:
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def projection_matrix(self, aspect: float) -> glm.mat4x4:
        return glm.perspective(glm.radians(self.fov), aspect, 0.01, 100.0)

    def rotate(self, dx: float, dy: float) -> None:
        self.yaw += dx * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * self.sensitivity))
        self._update_vectors()

    def move(self, forward: int, strafe: int, dt: float) -> None:
        flat_front = glm.normalize(glm.vec3(self.front.x, 0.0, self.front.z))
        direction = flat_front * forward + self.right * strafe
        if glm.length(direction) > 0:
            self.position += glm.normalize(direction) * self.speed * dt


class IsometricRotationDirection(Enum):
    Right = auto()
    Left = auto()


class IsometricCamera:
    type: CameraType = CameraType.Isometric
    rotation_speed = 0.06
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
        return glm.ortho(-z * aspect, z * aspect, -z, z, -1.0, 100.0)

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

    def set_zoom(self, zoom: float = 1) -> None:
        self.zoom_level = max(0.05, zoom)  # zoom <= 0 inverteria a imagem
