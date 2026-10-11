from pyglm import glm


class Camera:
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
        self.proj = glm.ortho(
            -self.zoom_level * self.aspect_ratio,
            self.zoom_level * self.aspect_ratio,
            -self.zoom_level,
            self.zoom_level,
            -1.0,
            100.0,
        )
        self.pv = self.proj * self.view

    def move_at(self, x_pos: float = 0.0, y_pos: float = 0.0, z_pos: float = 0.0):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos
        self.pv = glm.translate(self.pv, glm.vec3(self.x_pos, self.y_pos, self.z_pos))

    def translate(self, x=0.0, y=0.0, z=0.0):
        self.x_pos += x
        self.y_pos += y
        self.z_pos += z
        self.pv = glm.translate(self.pv, glm.vec3(self.x_pos, self.y_pos, self.z_pos))

    def rotate(self, angle=0.0, x_angle=0.0, y_angle=0.0, z_angle=0.0):
        self.xa = x_angle
        self.ya = y_angle
        self.za = z_angle
        self.pv = self.pv * glm.rotate(angle, glm.vec3(self.xa, self.ya, self.za))

    def set_zoom(self, zoom: float = 1):
        self.zoom_level = zoom
        # TODO: Implementar o Zoom de camera corretamente
        self.pv = self.proj * self.view
