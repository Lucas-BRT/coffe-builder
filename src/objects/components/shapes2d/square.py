from __future__ import annotations

from dataclasses import dataclass, field

from pyglm import glm

from src.objects import Mesh, Object


def _square_mesh(side: float) -> Mesh:
    return Mesh.from_vertices(Square.build_vertices(side))


@dataclass
class Square(Object):
    """Quadrado no plano XY, centrado na origem.

    side: comprimento do lado
    """

    side: float = 1.0

    # Redefine o campo do pai: o Square cria a malha sozinho, então ela
    # não entra mais no __init__.
    mesh: Mesh = field(init=False)

    def __post_init__(self) -> None:
        if self.side <= 0:
            raise ValueError("Side should be positive")
        self.mesh = _square_mesh(self.side)
        super().__post_init__()

    @staticmethod
    def build_vertices(side: float) -> glm.array[glm.vec3]:
        """
        É staticmethod para poder ser usado sem criar um Square.
        """
        h = side / 2
        return glm.array(
            [
                # botton left triangle
                glm.vec3(-h, h, 0),
                glm.vec3(-h, -h, 0),
                glm.vec3(h, -h, 0),
                # top right triangle
                glm.vec3(-h, h, 0),
                glm.vec3(h, -h, 0),
                glm.vec3(h, h, 0),
            ]
        )

    def vertices(self) -> glm.array[glm.vec3]:
        return Square.build_vertices(self.side)
