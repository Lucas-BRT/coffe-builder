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
from pyglm import glm


class IsometricCamera:
    def __init__(
        self,
        x_pos: float = 1,
        y_pos: float = 1,
        z_pos: float = 1,
        zoom_level: float = 1,
        lokin_at_x: float = 1,
        lokin_at_y: float = 1,
        lokin_at_z: float = 1,
        aspect_ratio: float = 1,
    ):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos

        self.zoom_level = zoom_level

        self.lokin_at_x = lokin_at_x
        self.lokin_at_y = lokin_at_y
        self.lokin_at_z = lokin_at_z

        self.aspect_ratio = aspect_ratio

        # câmera na diagonal (1,1,1) olhando para a origem
        self.view = glm.lookAt(
            glm.vec3(1.0, 1.0, 1.0),  # posição
            glm.vec3(0.0, 0.0, 0.0),  # alvo
            glm.vec3(0.0, 1.0, 0.0),  # up
        )

    def view_matrix(self):
        return self.view

    def projection_matrix(self, aspect):
        z = self.zoom_level
        return glm.ortho(-z * aspect, z * aspect, -z, z, -1.0, 100.0)

    def move_at(self, x_pos: float = 0.0, y_pos: float = 0.0, z_pos: float = 0.0):
        self.translate(x_pos, y_pos, z_pos)

    def translate(self, x=0.0, y=0.0, z=0.0):
        self.view = glm.translate(self.view, glm.vec3(x, y, z))

    def rotate(self, angle=0.0, x_angle=0.0, y_angle=0.0, z_angle=0.0):
        self.view = self.view * glm.rotate(angle, glm.vec3(x_angle, y_angle, z_angle))

    def set_zoom(self, zoom: float = 1):
        self.zoom_level = max(0.05, zoom)  # zoom <= 0 inverteria a imagem
