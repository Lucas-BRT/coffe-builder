from dataclasses import dataclass, field
from typing import Dict, Optional

from OpenGL.GL import *
from pyglm import glm


@dataclass(frozen=True)
class Mesh:
    """Geometria que já foi enviada para a GPU. Podemos compartilhar entre objetos"""

    vao: int
    vbo: int
    vertex_count: int

    @classmethod
    def from_vertices(cls, vertices: glm.array) -> "Mesh":
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

    def matrix(self) -> glm.mat4:
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
    "BLUE": Color(1, 0, 1, 1),
    "WHITE": Color(1, 1, 1, 1),
    "BLACK": Color(1, 1, 1, 1),
}


@dataclass
class Object:
    mesh: Mesh
    transform: Transform = field(default_factory=Transform)
    color: Color = field(default_factory=lambda: COLORS["WHITE"])
    original_color: Color = field(init=False)

    def __post_init__(self):
        self.original_color = self.color

    @property
    def model(self):
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

    def render(self, renderer) -> None:
        model = self.model

        glPolygonMode(GL_FRONT_AND_BACK, renderer.render_mode.value)
        glUniformMatrix4fv(renderer.model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glUniform4f(renderer.color_loc, *self.color.to_gpu())
        glBindVertexArray(self.mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count)
