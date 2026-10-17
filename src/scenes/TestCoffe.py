import glm
from OpenGL.GL import *

from src.objects.chair import Chair
from src.scenes import Scene


class TestCoffe(Scene):
    def __init__(self):
        vertex = glm.array(Chair.vertex())

        vao = glGenVertexArrays(1)

        super().__init__(vao, len(vertex))

        self.vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex.ptr, GL_STATIC_DRAW)
        glVertexAttribPointer(0, len(vertex[0]), GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)

    def render(self):
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glBindVertexArray(obj.vao)
        glPolygonMode(GL_FRONT_AND_BACK, self.render_mode.value)
        glDrawArrays(GL_TRIANGLES, 0, obj.vertex_count)
