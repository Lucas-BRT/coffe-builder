from dataclasses import dataclass, field
from typing import List

from src.objects import Entity


@dataclass
class Scene:
    objects: List[Entity] = field(default_factory=list)
    iso_zoom: float = 1.0

    def render(self, renderer) -> None:
        for obj in self.objects:
            obj.render(renderer)
