from pyglm import glm

from src.objects import COLORS, Transform
from src.objects.components import Block, Circle, Cylinder, Sphere, Square, Triangle
from src.scenes import Scene


def at(
    x: float, y: float, z: float, rx: float = 0, ry: float = 0, rz: float = 0
) -> Transform:
    """Atalho para não repetir Transform(position=..., rotation=...) em toda linha"""
    return Transform(position=glm.vec3(x, y, z), rotation=glm.dvec3(rx, ry, rz))


class DebugScene(Scene):
    """
    Cena para testar renderização: um chão com formas espalhadas em fileiras.
    Tudo cabe na isométrica com zoom 1 (mais ou menos entre -0.8 e 0.8 em X e Z),
    e os objetos 3D ficam apoiados no chão (y = metade da altura).
    """

    def __init__(self) -> None:
        super().__init__()

        # chão, deitado no plano XZ
        self.objects.append(
            Square(side=1.6, transform=at(0, 0, 0, rx=-90), color=COLORS["GRAY"])
        )

        # fileira de trás: formas 2D em pé, de frente para +Z
        self.objects += [
            Triangle.equilateral(
                0.3, transform=at(-0.55, 0.18, -0.7), color=COLORS["YELLOW"]
            ),
            Circle(radius=0.15, transform=at(-0.2, 0.18, -0.7), color=COLORS["CYAN"]),
            # Circle com poucos segmentos vira polígono regular
            Circle(
                radius=0.15,
                segments=6,
                transform=at(0.15, 0.18, -0.7),
                color=COLORS["MAGENTA"],
            ),
            # Square girado 45° no próprio plano vira um losango
            Square(side=0.25, transform=at(0.5, 0.18, -0.7, rz=45), color=COLORS["PURPLE"]),
        ]

        # fileira do meio: blocos
        self.objects += [
            Block.cube(0.3, transform=at(-0.5, 0.15, -0.3), color=COLORS["RED"]),
            Block(
                width=0.15,
                height=0.5,
                depth=0.15,
                transform=at(0.5, 0.25, -0.3),
                color=COLORS["BLUE"],
            ),
        ]

        # centro: uma mesinha de café montada com várias peças
        table_height = 0.3
        for x in (-0.2, 0.2):
            for z in (-0.2, 0.2):
                self.objects.append(
                    Cylinder(
                        radius=0.025,
                        height=table_height,
                        segments=12,
                        transform=at(x, table_height / 2, z),
                        color=COLORS["BROWN"],
                    )
                )
        self.objects += [
            Block(
                width=0.5,
                height=0.04,
                depth=0.5,
                transform=at(0, table_height + 0.02, 0),
                color=COLORS["BROWN"],
            ),
            # xícara em cima da mesa
            Cylinder(
                radius=0.05,
                height=0.08,
                transform=at(0.08, table_height + 0.04 + 0.04, 0.05),
                color=COLORS["WHITE"],
            ),
        ]

        # fileira da frente: formas curvas e um cubo girado no ar
        self.objects += [
            Sphere(radius=0.15, transform=at(-0.5, 0.15, 0.5), color=COLORS["GREEN"]),
            Cylinder(
                radius=0.12,
                height=0.35,
                transform=at(0.5, 0.175, 0.5),
                color=COLORS["ORANGE"],
            ),
            # Cylinder com poucos segmentos vira prisma
            Cylinder(
                radius=0.1,
                height=0.2,
                segments=6,
                transform=at(0, 0.1, 0.55),
                color=COLORS["CYAN"],
            ),
            Block.cube(
                0.15, transform=at(0, 0.5, 0.5, rx=30, ry=45), color=COLORS["YELLOW"]
            ),
        ]
