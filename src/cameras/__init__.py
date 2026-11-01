from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

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
