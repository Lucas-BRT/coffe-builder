from OpenGL.GL import *
from pyglm import glm

from src.objects import Object
from src.objects.components.block import Block


class Chair(Object):
    def __init__(self, width=0.5, height=0.5, depth=0.5, x=1.0, y=1.0, z=1.0):
        vertex = glm.array(Chair.vertex())

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
        width: float = 0.5, height: float = 0.5, depth: float = 0.5, x=0.0, y=0, z=0
    ):
        leg_spacing = 0.3
        leg_height = 0.25
        leg_width = 0.05
        seat_size = 2 * (x + 2 * leg_width)
        seat_height = 0.05
        seat_y = leg_height + (seat_height)

        leg = glm.array(
            Block.vertex(height=leg_height, width=leg_width, depth=leg_width)
        )

        leg1 = leg + glm.vec3(x + leg_spacing, y, z + leg_spacing)
        leg2 = leg + glm.vec3(x - leg_spacing, y, z - leg_spacing)
        leg3 = leg + glm.vec3(x + leg_spacing, y, z - leg_spacing)
        leg4 = leg + glm.vec3(x - leg_spacing, y, z + leg_spacing)

        seat = glm.array(
            Block.vertex(height=seat_height, width=seat_size, depth=seat_size)
        )
        seat = seat + glm.vec3(x, y + seat_y, z)

        return [*leg1, *leg2, *leg3, *leg4, *seat]
