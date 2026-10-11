from OpenGL.GL import *
from pyglm import glm

from src.objects import Object


class Triangle(Object):
    def __init__(self, x=0.0, y=0.0, size=0.05):
        vertex = glm.array(
            # [Vertex(-0.5, -0.5, 0.0), Vertex(0.5, -0.5, 0.0), Vertex(0.0, 0.5, 0.0)],
            # dtype=np.float32,
            glm.vec3(0.0, size * 1.2, 0.0),
            glm.vec3(size, -size, 0.0),
            glm.vec3(-size, -size, 0.0),
        )

        vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex.ptr, GL_STATIC_DRAW)
        glVertexAttribPointer(0, len(vertex[0]), GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)

        super().__init__(vao, len(vertex), model=glm.mat4(1))
