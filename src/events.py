from dataclasses import dataclass

from src.camera import IsometricRotationDirection
from src.objects import Object


@dataclass
class Event:
    pass


@dataclass
class CloseApplication(Event):
    pass


@dataclass
class SpawObject(Event):
    object: Object


@dataclass
class RemoveLastObject(Event):
    pass


@dataclass
class SelectNextObject(Event):
    pass


@dataclass
class MoveSelectedObject(Event):
    dx: float = 0.0
    dy: float = 0.0
    dz: float = 0.0


@dataclass
class ChangeCameraRequest(Event):
    pass


@dataclass
class MoveCamera(Event):
    # direções vindas do teclado: 1, 0 ou -1
    forward: int
    strafe: int
    dt: float


@dataclass
class RotateCamera(Event):
    # deslocamento do mouse desde o último movimento, usado pela câmera em perspectiva
    dx: float
    dy: float


@dataclass
class RotateIsometricCamera(Event):
    # por padrão, vamos mover apenas no eixo Z, rotacionando ao redor do centro
    # alternando de valores negativos ou positivos para indicar a direação
    direction: IsometricRotationDirection


@dataclass
class UpdateZoomLevel(Event):
    # negativo aproxima, positivo afasta
    amount: float
