import math
from pyglm import glm

class Camera:
    def __init__(self, position=(0.0, 0.2, 0.2), yaw=-90, pitch=0.0):
        self.position = glm.vec3(*position)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 0.4        # unidades por SEGUNDO
        self.sensitivity = 0.1
        self.fov = 70.0
        self._update_vectors()

    def _update_vectors(self):
        yaw, pitch = math.radians(self.yaw), math.radians(self.pitch)
        self.front = glm.normalize(glm.vec3(
            math.cos(yaw) * math.cos(pitch),
            math.sin(pitch),
            math.sin(yaw) * math.cos(pitch),
        ))
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.cross(self.right, self.front)


    def view_matrix(self):
        return glm.lookAt(self.position, self.position+self.front, self.up)

    def projection_matrix(self, aspect):
        return glm.perspective(glm.radians(self.fov), aspect, 0.01, 100.0)

    def rotate(self, dx, dy):
        self.yaw += dx * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * self.sensitivity))
        self._update_vectors()

    def move(self, forward, strafe, dt):
        flat_front = glm.normalize(glm.vec3(self.front.x, 0.0, self.front.z))
        direction = flat_front * forward + self.right * strafe
        if glm.length(direction) > 0:
            self.position += glm.normalize(direction) * self.speed * dt
