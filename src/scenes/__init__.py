from dataclasses import dataclass, field
from typing import List

from pyglm import glm

from src.objects import Object

from . import *


@dataclass
class Scene:
    vao: int
    vertex_count: int
    model: glm.f32mat4
    objects: List[Object] = field(default_factory=list)
    x: float = 0
    xa: float = 0
    y: float = 0
    ya: float = 0
    z: float = 0
    za: float = 0

    def model(width: float = 1, height: float = 0.5, depth: float = 0.5):
        pass
