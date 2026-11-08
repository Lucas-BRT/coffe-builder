from dataclasses import dataclass, field
from typing import List, Tuple

from pyglm import glm

from src.objects import Color, Entity


def scaled(color: Color, intensity: float) -> Color:
    return Color(color.r * intensity, color.g * intensity, color.b * intensity, color.a)

# precisa bater com MAX_LIGHTS em shaders/main.frag
MAX_LIGHTS = 8


@dataclass
class Scene:
    objects: List[Entity] = field(default_factory=list)
    iso_zoom: float = 1.0
    # força do astro (sol/lua); como ele não perde força com a distância, é bem menor
    # que a de uma lâmpada próxima
    sky_intensity: float = 0.35

    def light_sources(self) -> List[Tuple[glm.vec3, Color, float]]:
        """
        (posição no mundo, cor, atenuação) de cada luz acesa: o astro da cena, se
        houver (self.light, sem atenuação por distância), e todo Entity com emits_light ligado (as luminárias)
        """
        sources: List[Tuple[glm.vec3, Color, float]] = []
        sun = getattr(self, "light", None)
        if sun is not None:
            sources.append(
                (sun.transform.position, scaled(sun.color, self.sky_intensity), 0.0)
            )

        def visit(entity: Entity, parent) -> None:
            world = entity.world_matrix(parent)
            if getattr(entity, "emits_light", False) and getattr(entity, "on", True):
                offset = entity.light_offset
                sources.append(
                    (glm.vec3(world * glm.vec4(offset.x, offset.y, offset.z, 1.0)), scaled(entity.light_color, entity.light_intensity), 1.0)
                )
            for part in getattr(entity, "parts", ()):
                visit(part, world)

        for obj in self.objects:
            visit(obj, None)
        return sources[:MAX_LIGHTS]

    def render(self, renderer) -> None:
        for obj in self.objects:
            if not getattr(obj, "emissive", False) and getattr(
                obj, "self_shadow_enabled", True
            ):
                renderer.render_self_shadow(obj)
            obj.render(renderer)
