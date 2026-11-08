from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from pyglm import glm

from src.objects import Mesh, Object, transform_vertices
from src.objects.components.shapes2d.circle import Circle


def _cylinder_mesh(
    radius: float, height: float, segments: int, tile: Optional[float] = None
) -> Mesh:
    return Mesh.from_vertices(
        Cylinder.build_vertices(radius, height, segments),
        Cylinder.build_uvs(radius, height, segments, tile),
    )


@dataclass
class Cylinder(Object):
    """Cilindro em pé (eixo Y), centrado na origem.

    radius:   raio das tampas
    height:   altura
    segments: quantas faces formam a lateral; poucos viram prisma
              (3 -> prisma triangular, 6 -> prisma hexagonal...)
    """

    radius: float = 0.5
    height: float = 1.0
    segments: int = 32
    uv_tile: Optional[float] = None

    # Redefine o campo do pai: o Cylinder cria a malha sozinho, então ela
    # não entra mais no __init__.
    mesh: Mesh = field(init=False)

    def __post_init__(self) -> None:
        if self.radius <= 0 or self.height <= 0:
            raise ValueError("Radius and Height should be positive")
        if self.segments < 3:
            raise ValueError("Cylinder needs at least 3 segments")
        self.mesh = _cylinder_mesh(self.radius, self.height, self.segments, self.uv_tile)
        super().__post_init__()

    def apply_texture(self, texture, tile=None) -> None:
        old, self.uv_tile = self.mesh, tile
        self.mesh = _cylinder_mesh(self.radius, self.height, self.segments, tile)
        old.delete()
        self.texture = texture

    @staticmethod
    def build_vertices(radius: float, height: float, segments: int) -> glm.array[glm.vec3]:
        """
        É staticmethod para poder ser usado sem criar um Cylinder.

        As tampas são Circles deitados no plano XZ; a lateral é uma faixa de
        retângulos (2 triângulos cada) ligando a borda de baixo à de cima.
        """
        h = height / 2
        x_axis = glm.vec3(1, 0, 0)

        circle = Circle.build_vertices(radius, segments)
        top = transform_vertices(
            circle,
            glm.rotate(glm.translate(glm.vec3(0, h, 0)), glm.radians(-90), x_axis),
        )
        bottom = transform_vertices(
            circle,
            glm.rotate(glm.translate(glm.vec3(0, -h, 0)), glm.radians(90), x_axis),
        )

        side: List[glm.vec3] = []
        for i in range(segments):
            a = 2 * glm.pi() * i / segments
            b = 2 * glm.pi() * (i + 1) / segments
            bottom_a = glm.vec3(radius * glm.cos(a), -h, radius * glm.sin(a))
            bottom_b = glm.vec3(radius * glm.cos(b), -h, radius * glm.sin(b))
            top_a = glm.vec3(bottom_a.x, h, bottom_a.z)
            top_b = glm.vec3(bottom_b.x, h, bottom_b.z)
            side += [bottom_a, bottom_b, top_b, bottom_a, top_b, top_a]

        return glm.array(list(top) + list(bottom) + side)

    @staticmethod
    def build_uvs(
        radius: float, height: float, segments: int, tile: Optional[float] = None
    ) -> glm.array[glm.vec2]:
        """
        Mesma ordem de build_vertices. Tampas: projeção por cima. Lateral: a imagem
        dá a volta no cilindro. tile é o tamanho em metros de uma repetição; sem
        ele, a imagem cobre a tampa inteira e a lateral inteira uma vez.
        """
        cap_scale = tile or 2 * radius
        circumference = 2 * glm.pi() * radius
        around = circumference / (tile or circumference)
        up = height / (tile or height)

        uvs: List[glm.vec2] = []
        for _ in range(2):  # tampa de cima e de baixo
            for i in range(segments):
                a = 2 * glm.pi() * i / segments
                b = 2 * glm.pi() * (i + 1) / segments
                for angle, r in ((0.0, 0.0), (a, radius), (b, radius)):
                    uvs.append(
                        glm.vec2(
                            0.5 + r * glm.cos(angle) / cap_scale,
                            0.5 + r * glm.sin(angle) / cap_scale,
                        )
                    )
        for i in range(segments):
            ua, ub = around * i / segments, around * (i + 1) / segments
            uvs += [
                glm.vec2(ua, 0), glm.vec2(ub, 0), glm.vec2(ub, up),
                glm.vec2(ua, 0), glm.vec2(ub, up), glm.vec2(ua, up),
            ]
        return glm.array(uvs)

    def vertices(self) -> glm.array[glm.vec3]:
        return Cylinder.build_vertices(self.radius, self.height, self.segments)
