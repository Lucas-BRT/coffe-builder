from dataclasses import dataclass, field
from typing import List

from src.objects import Entity


@dataclass
class Scene:
    objects: List[Entity] = field(default_factory=list)
    iso_zoom: float = 1.0

    def render(self, renderer) -> None:
        for obj in self.objects:
            if not getattr(obj, "emissive", False) and getattr(
                obj, "self_shadow_enabled", True
            ):
                renderer.render_self_shadow(obj)
            obj.render(renderer)
