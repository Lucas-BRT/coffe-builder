from dataclasses import dataclass

from OpenGL.GL import *
from pyglm import glm


@dataclass
class Object:
    vao: int
    vertex_count: int
    model: glm.f32mat4
    x: float = 0
    xa: float = 0
    y: float = 0
    ya: float = 0
    z: float = 0
    za: float = 0

    def move_at(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
        self.model = glm.translate(self.model, glm.vec3(self.x, self.y, self.z))

    def translate(self, x=0.0, y=0.0, z=0.0):
        self.x += x
        self.y += y
        self.z += z
        self.model = glm.translate(self.model, glm.vec3(self.x, self.y, self.z))

    def rotate(self, angle=0.0, x_angle=0.0, y_angle=0.0, z_angle=0.0):
        self.xa = x_angle
        self.ya = y_angle
        self.za = z_angle
        self.model = self.model * glm.rotate(angle, glm.vec3(self.xa, self.ya, self.za))
