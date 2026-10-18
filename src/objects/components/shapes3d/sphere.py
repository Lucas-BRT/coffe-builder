from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from pyglm import glm

from src.objects import Mesh, Object


def _sphere_mesh(radius: float, stacks: int, sectors: int) -> Mesh:
    return Mesh.from_vertices(Sphere.build_vertices(radius, stacks, sectors))


@dataclass
class Sphere(Object):
    """Esfera centrada na origem, montada em "gomos" como um globo.

    radius:  raio
    stacks:  quantas faixas horizontais (latitude), de polo a polo
    sectors: quantas fatias verticais (longitude) ao redor do eixo Y
    """

    radius: float = 0.5
    stacks: int = 16
    sectors: int = 32

    # Redefine o campo do pai: a Sphere cria a malha sozinha, então ela
    # não entra mais no __init__.
    mesh: Mesh = field(init=False)

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError("Radius should be positive")
        if self.stacks < 2 or self.sectors < 3:
            raise ValueError("Sphere needs at least 2 stacks and 3 sectors")
        self.mesh = _sphere_mesh(self.radius, self.stacks, self.sectors)
        super().__post_init__()

    @staticmethod
    def build_vertices(radius: float, stacks: int, sectors: int) -> glm.array[glm.vec3]:
        """
        É staticmethod para poder ser usado sem criar uma Sphere.
        """

        def point(stack: int, sector: int) -> glm.vec3:
            phi = glm.pi() * stack / stacks  # 0 no polo de cima, pi no de baixo
            theta = 2 * glm.pi() * sector / sectors
            return glm.vec3(
                radius * glm.sin(phi) * glm.cos(theta),
                radius * glm.cos(phi),
                radius * glm.sin(phi) * glm.sin(theta),
            )

        vertices: List[glm.vec3] = []
        for i in range(stacks):
            for j in range(sectors):
                p1, p2 = point(i, j), point(i + 1, j)
                p3, p4 = point(i + 1, j + 1), point(i, j + 1)
                # nos polos um dos triângulos degenera numa linha e não é desenhado
                vertices += [p1, p2, p3, p1, p3, p4]
        return glm.array(vertices)

    def vertices(self) -> glm.array[glm.vec3]:
        return Sphere.build_vertices(self.radius, self.stacks, self.sectors)
