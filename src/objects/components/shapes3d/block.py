from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from pyglm import glm

from src.objects import Mesh, Object, transform_vertices
from src.objects.components.shapes2d.square import Square


def _block_mesh(width: float, height: float, depth: float) -> Mesh:
    return Mesh.from_vertices(Block.build_vertices(width, height, depth))


@dataclass
class Block(Object):
    """Paralelepípedo centrado na origem.

    width:  tamanho no eixo X
    height: tamanho no eixo Y
    depth:  tamanho no eixo Z
    """

    width: float = 1.0
    height: float = 1.0
    depth: float = 1.0

    # Redefine o campo do pai: o Block cria a malha sozinho, então ela
    # não entra mais no __init__.
    mesh: Mesh = field(init=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0 or self.depth <= 0:
            raise ValueError("Width, Height and Depth should be positive")
        self.mesh = _block_mesh(self.width, self.height, self.depth)
        super().__post_init__()

    @classmethod
    def cube(cls, side: float = 1.0, **kwargs) -> Block:
        return cls(width=side, height=side, depth=side, **kwargs)

    @staticmethod
    def build_vertices(width: float, height: float, depth: float) -> glm.array[glm.vec3]:
        """
        É staticmethod para poder ser usado sem criar um Block

        Cada face é um Square de lado 1 (no plano XY), esticado para o tamanho
        da face, girado para a direção certa e empurrado até a borda do bloco

        sim, essa volta toda para não ter que escrever umas 500 linhas definindo
        vértices
        """
        w, h, d = width / 2, height / 2, depth / 2
        x_axis, y_axis = glm.vec3(1, 0, 0), glm.vec3(0, 1, 0)

        def face(
            offset: glm.vec3, angle: float, axis: glm.vec3, size_x: float, size_y: float
        ) -> List[glm.vec3]:
            matrix = glm.translate(offset)
            matrix = glm.rotate(matrix, glm.radians(angle), axis)
            matrix = glm.scale(matrix, glm.vec3(size_x, size_y, 1.0))
            return list(transform_vertices(Square.build_vertices(1.0), matrix))

        return glm.array(
            face(glm.vec3(0, 0, d), 0, y_axis, width, height)  # frente
            + face(glm.vec3(0, 0, -d), 180, y_axis, width, height)  # trás
            + face(glm.vec3(w, 0, 0), 90, y_axis, depth, height)  # direita
            + face(glm.vec3(-w, 0, 0), -90, y_axis, depth, height)  # esquerda
            + face(glm.vec3(0, h, 0), -90, x_axis, width, depth)  # topo
            + face(glm.vec3(0, -h, 0), 90, x_axis, width, depth)  # base
        )

    def vertices(self) -> glm.array[glm.vec3]:
        return Block.build_vertices(self.width, self.height, self.depth)
