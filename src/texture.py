from enum import Enum
from pathlib import Path

from OpenGL.GL import *
from PIL import Image, ImageOps

TEXTURES_DIR = Path(__file__).resolve().parent.parent / "assets" / "textures"


class Texture:
    def __init__(self, file_name: str, pixelated: bool = False) -> None:
        # RGBA sempre: evita ter que escolher GL_RGB ou GL_RGBA pelo número de canais
        image = Image.open(TEXTURES_DIR / file_name).convert("RGBA")
        # o tutorial chama stbi_set_flip_vertically_on_load: a imagem tem a origem
        # em cima e o OpenGL espera embaixo
        image = ImageOps.flip(image)
        width, height = image.size

        self.id = int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        if pixelated:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, image.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)

    def bind(self, unit: int = 0) -> None:
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)
