from typing import Tuple

from pyglm import glm

from src.cameras import Camera, CameraType


class PerspectiveCamera(Camera):
    type: CameraType = CameraType.Perspective

    def __init__(
        self,
        position: Tuple[float, float, float] = (0.9, 1.6, -1.2),
        yaw: float = 90,
        pitch: float = -20,
    ) -> None:
        self.position = glm.vec3(*position)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 1.5  # unidades por SEGUNDO
        self.sensitivity = 0.1
        self.fov = 70.0
        self._update_vectors()

    def _update_vectors(self) -> None:
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
        self.front = glm.normalize(
            glm.vec3(
                glm.cos(yaw) * glm.cos(pitch),
                glm.sin(pitch),
                glm.sin(yaw) * glm.cos(pitch),
            )
        )
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.cross(self.right, self.front)

    def view_matrix(self) -> glm.mat4x4:
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def projection_matrix(self, aspect: float) -> glm.mat4x4:
        return glm.perspective(glm.radians(self.fov), aspect, 0.01, 100.0)

    def rotate(self, dx: float, dy: float) -> None:
        self.yaw += dx * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * self.sensitivity))
        self._update_vectors()

    def move(self, forward: int, strafe: int, dt: float) -> None:
        flat_front = glm.normalize(glm.vec3(self.front.x, 0.0, self.front.z))
        direction = flat_front * forward + self.right * strafe
        if glm.length(direction) > 0:
            self.position += glm.normalize(direction) * self.speed * dt
