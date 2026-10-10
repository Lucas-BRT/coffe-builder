from OpenGL.GL import *
from pyglm import glm

from src.objects import Object


class Square(Object):
    def __init__(self, x=1.0, y=1.0, z=1.0):
        vertex = glm.array(
            # botton left triangle
            glm.vec3(-0.5, 0.5, 0),
            glm.vec3(-0.5, -0.5, 0),
            glm.vec3(0.5, -0.5, 0),
            # top right triangle
            glm.vec3(-0.5, 0.5, 0),
            glm.vec3(0.5, -0.5, 0),
            glm.vec3(0.5, 0.5, 0),
        )

        vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex.ptr, GL_STATIC_DRAW)
        glVertexAttribPointer(0, len(vertex[0]), GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)
        super().__init__(vao, len(vertex), glm.mat4(1.0))
