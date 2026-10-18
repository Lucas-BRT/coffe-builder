from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from pyglm import glm

from src.objects import Mesh, Object


def _circle_mesh(radius: float, segments: int) -> Mesh:
    return Mesh.from_vertices(Circle.build_vertices(radius, segments))


@dataclass
class Circle(Object):
    """Círculo no plano XY, centrado na origem.

    radius:   raio
    segments: quantos triângulos formam o contorno; poucos viram polígono
              regular (3 -> triângulo, 6 -> hexágono...)
    """

    radius: float = 0.5
    segments: int = 32

    # Redefine o campo do pai: o Circle cria a malha sozinho, então ela
    # não entra mais no __init__.
    mesh: Mesh = field(init=False)

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError("Radius should be positive")
        if self.segments < 3:
            raise ValueError("Circle needs at least 3 segments")
        self.mesh = _circle_mesh(self.radius, self.segments)
        super().__post_init__()

    @staticmethod
    def build_vertices(radius: float, segments: int) -> glm.array[glm.vec3]:
        """
        É staticmethod para poder ser usado sem criar um Circle.
        Cada fatia é um triângulo: centro -> ponto da borda -> próximo ponto.
        """
        center = glm.vec3(0.0)
        rim = [
            glm.vec3(
                radius * glm.cos(2 * glm.pi() * i / segments),
                radius * glm.sin(2 * glm.pi() * i / segments),
                0.0,
            )
            for i in range(segments)
        ]
        vertices: List[glm.vec3] = []
        for i in range(segments):
            vertices += [center, rim[i], rim[(i + 1) % segments]]
        return glm.array(vertices)

    def vertices(self) -> glm.array[glm.vec3]:
        return Circle.build_vertices(self.radius, self.segments)
