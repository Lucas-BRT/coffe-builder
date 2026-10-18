from dataclasses import dataclass, field
from typing import List

from pyglm import glm

from src.objects import Object


@dataclass
class Scene:
    objects: List[Object] = field(default_factory=list)

    def render(self, renderer) -> None:
        for obj in self.objects:
            obj.render(renderer)
