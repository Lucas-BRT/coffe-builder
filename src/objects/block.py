from OpenGL.GL import *
from pyglm import glm

from src.objects import COLORS, Color, Object


class Block(Object):
    def __init__(
        self,
        width=0.5,
        height=0.5,
        depth=0.5,
        x=1.0,
        y=1.0,
        z=1.0,
        color: Color = COLORS["WHITE"],
    ):
        vertex = glm.array(
            # frente (z = +depth)
            glm.vec3(-width, height, depth),
            glm.vec3(-width, -height, depth),
            glm.vec3(width, -height, depth),
            glm.vec3(-width, height, depth),
            glm.vec3(width, -height, depth),
            glm.vec3(width, height, depth),
            # trás (z = -depth)
            glm.vec3(width, height, -depth),
            glm.vec3(width, -height, -depth),
            glm.vec3(-width, -height, -depth),
            glm.vec3(width, height, -depth),
            glm.vec3(-width, -height, -depth),
            glm.vec3(-width, height, -depth),
            # topo (y = +height)
            glm.vec3(-width, height, -depth),
            glm.vec3(-width, height, depth),
            glm.vec3(width, height, depth),
            glm.vec3(-width, height, -depth),
            glm.vec3(width, height, depth),
            glm.vec3(width, height, -depth),
            # base (y = -height)
            glm.vec3(-width, -height, depth),
            glm.vec3(-width, -height, -depth),
            glm.vec3(width, -height, -depth),
            glm.vec3(-width, -height, depth),
            glm.vec3(width, -height, -depth),
            glm.vec3(width, -height, depth),
            # direita (x = +width)
            glm.vec3(width, height, depth),
            glm.vec3(width, -height, depth),
            glm.vec3(width, -height, -depth),
            glm.vec3(width, height, depth),
            glm.vec3(width, -height, -depth),
            glm.vec3(width, height, -depth),
            # esquerda (x = -width)
            glm.vec3(-width, height, -depth),
            glm.vec3(-width, -height, -depth),
            glm.vec3(-width, -height, depth),
            glm.vec3(-width, height, -depth),
            glm.vec3(-width, -height, depth),
            glm.vec3(-width, height, depth),
        )

        # super().__init__(vao, len(vertex), glm.mat4(1.0), color=glm.vec3(*color))

        super().__init__()
