from typing import List

from OpenGL.GL import *
from pyglm import glm

from src.objects import Object


class Block(Object):
    def __init__(self, width=0.5, height=0.5, depth=0.5, x=1.0, y=1.0, z=1.0):

        vertex = glm.array(*Block.vertex())

        vao = glGenVertexArrays(1)
        super().__init__(vao, len(vertex), glm.mat4(1.0))
        self.width = width
        self.height = height
        self.depth = depth
        self.x = x
        self.y = y
        self.z = z
        self.vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex.ptr, GL_STATIC_DRAW)
        glVertexAttribPointer(0, len(vertex[0]), GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)

    def vertex(
        width: float = 0.5,
        height: float = 0.5,
        depth: float = 0.5,
    ) -> List[glm.vec3]:
        return [
            # frente (z = +depth)
            glm.vec3(-(width), height, depth),
            glm.vec3(-(width), -height, depth),
            glm.vec3((width), -height, depth),
            glm.vec3(-(width), height, depth),
            glm.vec3((width), -height, depth),
            glm.vec3((width), height, depth),
            # trás (z = -depth)
            glm.vec3((width), height, -depth),
            glm.vec3((width), -height, -depth),
            glm.vec3(-(width), -height, -depth),
            glm.vec3((width), height, -depth),
            glm.vec3(-(width), -height, -depth),
            glm.vec3(-(width), height, -depth),
            # topo (y = +height)
            glm.vec3(-(width), height, -depth),
            glm.vec3(-(width), height, depth),
            glm.vec3((width), height, depth),
            glm.vec3(-(width), height, -depth),
            glm.vec3((width), height, depth),
            glm.vec3((width), height, -depth),
            # base (y = -height)
            glm.vec3(-(width), -height, depth),
            glm.vec3(-(width), -height, -depth),
            glm.vec3((width), -height, -depth),
            glm.vec3(-(width), -height, depth),
            glm.vec3((width), -height, -depth),
            glm.vec3((width), -height, depth),
            # direita (x = +(width + x))
            glm.vec3((width), height, depth),
            glm.vec3((width), -height, depth),
            glm.vec3((width), -height, -depth),
            glm.vec3((width), height, depth),
            glm.vec3((width), -height, -depth),
            glm.vec3((width), height, -depth),
            # esquerda (x = -(width + x))
            glm.vec3(-(width), height, -depth),
            glm.vec3(-(width), -height, -depth),
            glm.vec3(-(width), -height, depth),
            glm.vec3(-(width), height, -depth),
            glm.vec3(-(width), -height, depth),
            glm.vec3(-(width), height, depth),
        ]
