from __future__ import annotations

from dataclasses import dataclass, field

import glm

from src.objects import Mesh, Object


def _triangle_mesh(base: float, height: float, apex: float) -> Mesh:
    return Mesh.from_vertices(Triangle.build_vertices(base, height, apex))


@dataclass
class Triangle(Object):
    """Triângulo qualquer, já pronto para posicionar e desenhar.

    Herda de Object: transform, color, move_to, rotate_by, scale_to, render...

    A forma é definida por três números (o triângulo apoiado na base):
        base:   comprimento do lado de baixo
        height: altura, perpendicular à base
        apex:   posição horizontal do vértice de cima, como fração da base
                  0.0 / 1.0 -> retângulo
                  0.5       -> isósceles (equilátero se height = base·√3/2)
                  entre 0 e 1 -> acutângulo; < 0 ou > 1 -> obtusângulo

    Para mudar a forma depois de criado, crie outro Triangle.
    """

    base: float = 1.0
    height: float = 1.0
    apex: float = 0.5

    # Redefine o campo do pai: o Triangle cria a malha sozinho, então ela
    # não entra mais no __init__.
    mesh: Mesh = field(init=False)

    def __post_init__(self) -> None:
        if self.base <= 0 or self.height <= 0:
            raise ValueError("Base and Height should be positive")
        self.mesh = _triangle_mesh(self.base, self.height, self.apex)
        super().__post_init__()

    @classmethod
    def equilateral(cls, side: float = 1.0, **kwargs) -> Triangle:
        return cls(base=side, height=side * glm.sqrt(3) / 2, apex=0.5, **kwargs)

    @classmethod
    def isosceles(cls, base: float = 1.0, height: float = 1.0, **kwargs) -> Triangle:
        return cls(base=base, height=height, apex=0.5, **kwargs)

    @classmethod
    def right(cls, base: float = 1.0, height: float = 1.0, **kwargs) -> Triangle:
        return cls(base=base, height=height, apex=0.0, **kwargs)

    @classmethod
    def from_sides(cls, base: float, left: float, right: float, **kwargs) -> Triangle:
        """Constrói pelos três lados.

        left:  lado entre o vértice esquerdo da base e o vértice de cima
        right: lado entre o vértice direito da base e o vértice de cima
        """
        a, b, c = sorted((base, left, right))
        if a + b <= c:
            raise ValueError("this sides cannot build a triangle")
        # Lei dos cossenos: projeção do vértice de cima sobre a base.
        apex_x = (base**2 + left**2 - right**2) / (2 * base)
        height = glm.sqrt(left**2 - apex_x**2)
        return cls(base=base, height=height, apex=apex_x / base, **kwargs)

    @staticmethod
    def build_vertices(base: float, height: float, apex: float) -> glm.array:
        """
        É staticmethod para poder ser usado sem criar um Triangle.
        """
        a = glm.vec3(0.0, 0.0, 0.0)
        b = glm.vec3(base, 0.0, 0.0)
        c = glm.vec3(apex * base, height, 0.0)
        centroid = (a + b + c) / 3
        return glm.array(a - centroid, b - centroid, c - centroid)

    def vertices(self) -> glm.array:
        """Os vértices deste triângulo (espaço local)."""
        return Triangle.build_vertices(self.base, self.height, self.apex)
