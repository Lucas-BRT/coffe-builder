from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, cast

from OpenGL.GL import *
from pyglm import glm


@dataclass(frozen=True)
class Mesh:
    """Geometria que já foi enviada para a GPU. Podemos compartilhar entre objetos"""

    vao: int
    vbo: int
    vertex_count: int

    @classmethod
    def from_vertices(cls, vertices: glm.array[glm.vec3]) -> Mesh:
        """
        Retorna Mesh entre aspas pq aparentemente o Python é burro e não consegue instanciar
        a classe quando lê ela. Longa história, mas no final, tudo se resume a: Saudades
        C e C++.
        """

        if vertices.element_type is not glm.vec3:
            raise TypeError(
                f"esperava um glm.array de vec3 (float32), veio {vertices.element_type}"
            )

        vao = int(glGenVertexArrays(1))
        vbo = int(glGenBuffers(1))

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, glm.sizeof(glm.vec3), None)
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)

        return cls(vao=vao, vbo=vbo, vertex_count=len(vertices))

    def delete(self) -> None:
        """
        Só chame quando nenhum Object usar mais, se não os outros objetos vão sumir no melhor dos casos
        vo nem mentir que não testei, mas coisa boa não é, vide UseAfterFree em gerenciamento de memória
        do OS
        """
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])


@dataclass
class Transform:
    position: glm.vec3 = field(default_factory=glm.vec3)
    # usa Double Vec3 para ter mais presião, pq parece que em rotação os erros
    # se acumululam facilmente com baixa precição
    rotation: glm.dvec3 = field(default_factory=glm.dvec3)
    scale: glm.vec3 = field(default_factory=lambda: glm.vec3(1.0))

    @classmethod
    def at(
        cls,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        rx: float = 0.0,
        ry: float = 0.0,
        rz: float = 0.0,
    ) -> Transform:
        """Atalho para Transform(position=..., rotation=...), rotação em graus"""
        return cls(position=glm.vec3(x, y, z), rotation=glm.dvec3(rx, ry, rz))

    def matrix(self) -> glm.mat4x4:
        matrix = glm.translate(self.position)
        matrix = glm.rotate(
            matrix, glm.radians(self.rotation.z), glm.vec3(0.0, 0.0, 1.0)
        )
        matrix = glm.rotate(
            matrix, glm.radians(self.rotation.y), glm.vec3(0.0, 1.0, 0.0)
        )
        matrix = glm.rotate(
            matrix, glm.radians(self.rotation.x), glm.vec3(1.0, 0.0, 0.0)
        )
        matrix = glm.scale(matrix, self.scale)
        return matrix


def transform_vertices(
    vertices: glm.array[glm.vec3], matrix: glm.mat4x4
) -> glm.array[glm.vec3]:
    """
    Aplica a matriz em cada vértice. É o que permite montar uma forma a partir de
    outras, tipo as faces de um Block, que são Squares rotacionados e transladados
    """
    return glm.array(
        [glm.vec3(matrix * glm.vec4(v.x, v.y, v.z, 1.0)) for v in vertices]
    )


@dataclass(frozen=True)
class Color:
    r: float
    g: float
    b: float
    a: float

    def to_gpu(self) -> glm.vec4:
        return glm.vec4(self.r, self.g, self.b, self.a)


COLORS: Dict[str, Color] = {
    "RED": Color(1, 0, 0, 1),
    "GREEN": Color(0, 1, 0, 1),
    "BLUE": Color(0, 0, 1, 1),
    "WHITE": Color(1, 1, 1, 1),
    "BLACK": Color(0, 0, 0, 1),
    "GRAY": Color(0.5, 0.5, 0.5, 1),
    "YELLOW": Color(1, 1, 0, 1),
    "CYAN": Color(0, 1, 1, 1),
    "MAGENTA": Color(1, 0, 1, 1),
    "ORANGE": Color(1, 0.5, 0, 1),
    "PURPLE": Color(0.5, 0, 1, 1),
    "BROWN": Color(0.45, 0.28, 0.15, 1),
    "LIGHT_BROWN": Color(0.7, 0.52, 0.32, 1),
    "DARK_GRAY": Color(0.25, 0.25, 0.25, 1),
    "LIGHT_GRAY": Color(0.8, 0.8, 0.8, 1),
    "CREAM": Color(0.93, 0.88, 0.78, 1),
}


def compose(parent: glm.mat4x4, child: glm.mat4x4) -> glm.mat4x4:
    """
    Junta a matriz do pai com a do filho: o filho passa a viver no espaço do pai.
    O cast é só pro linter: os stubs do pyglm fazem o `*` entre matrizes cair na
    sobrecarga errada (mat4x2), mas é um mat4x4
    """
    return cast(glm.mat4x4, parent * child)


class Entity:
    """
    Tudo que tem posição no mundo e sabe se desenhar.

    pode ser um Object ou um Group (vários Entities que se movem juntos).

    Não é dataclass para permitir que cada componente declare o próprio
    `transform` sem bagunçar a ordem dos campos do __init__ delas.
    """

    transform: Transform

    def get_x(self) -> float:
        return self.transform.position.x

    def get_y(self) -> float:
        return self.transform.position.y

    def get_z(self) -> float:
        return self.transform.position.y

    @property
    def model(self) -> glm.mat4x4:
        return self.transform.matrix()

    def move_to(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.transform.position = glm.vec3(x, y, z)

    def move_by(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.transform.position += glm.vec3(dx, dy, dz)

    def rotate_to(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.transform.rotation = glm.dvec3(x, y, z)

    def scale_to(
        self, sx: float = 1.0, sy: Optional[float] = None, sz: Optional[float] = None
    ) -> None:
        """sx faz escala uniforme, os outros só se for fazer alguma escala diferente"""
        self.transform.scale = glm.vec3(
            sx, sx if sy is None else sy, sx if sz is None else sz
        )

    def world_matrix(self, parent: Optional[glm.mat4x4]) -> glm.mat4x4:
        """A matriz final: a própria, ou a própria dentro do espaço do pai"""
        return self.model if parent is None else compose(parent, self.model)

    def render(self, renderer, parent: Optional[glm.mat4x4] = None) -> None:
        raise NotImplementedError


@dataclass
class Object(Entity):
    mesh: Mesh
    transform: Transform = field(default_factory=Transform)
    color: Color = field(default_factory=lambda: COLORS["WHITE"])
    original_color: Color = field(init=False)

    def __post_init__(self) -> None:
        self.original_color = self.color

    def render(self, renderer, parent: Optional[glm.mat4x4] = None) -> None:
        model = self.world_matrix(parent)

        glPolygonMode(GL_FRONT_AND_BACK, renderer.render_mode.value)
        glUniformMatrix4fv(
            renderer.model_uniform_loc, 1, GL_FALSE, glm.value_ptr(model)
        )
        glUniform4f(renderer.color_uniform_loc, *self.color.to_gpu())
        glBindVertexArray(self.mesh.vao)
        # toda malha é uma lista de triângulos soltos (3 vértices cada)
        glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count)


@dataclass
class Group(Entity):
    """
    Vários Entities que se comportam como um só: mover/girar o grupo leva todas
    as partes junto. A posição de cada parte é relativa ao grupo, então dá pra
    montar uma cadeira em volta da origem e depois só colocar ela no lugar.

    Pode ter Groups dentro de Groups (uma mesa com cadeiras, por exemplo).
    """

    parts: List[Entity] = field(default_factory=list)
    transform: Transform = field(default_factory=Transform)

    def render(self, renderer, parent: Optional[glm.mat4x4] = None) -> None:
        model = self.world_matrix(parent)
        for part in self.parts:
            part.render(renderer, model)
