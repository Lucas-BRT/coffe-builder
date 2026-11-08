from __future__ import annotations

from functools import singledispatchmethod
from math import floor
from typing import List, Optional, Union

import glfw
from OpenGL.GL import *
from pyglm import glm

from src.cameras import CameraType
from src.cameras.isometric import IsometricCamera, IsometricRotationDirection
from src.cameras.perspective import PerspectiveCamera
from src.config import Config
from src.events import (
    ChangeCameraRequest,
    CloseApplication,
    Event,
    MoveCamera,
    MoveSelectedObject,
    GrabObject,
    InteractWithSelectedObject,
    ReleaseObject,
    RemoveSelectedObject,
    RotateCamera,
    RotateIsometricCamera,
    RotateSelectedObject,
    SelectNextObject,
    SpawObject,
    ToggleNight,
    UpdateZoomLevel,
)
from src.objects import COLORS, Color, Entity, Group, Transform
from src.objects.components import Block
from src.objects.cursor import CURSOR_GRID_STEP, Cursor
from src.scenes import Scene
from src.scenes.coffee_shop import CoffeeShopScene
from src.sidebar import Sidebar
from src.window import Window

AnyCamera = Union[IsometricCamera, PerspectiveCamera]

CURSOR_COLOR = Color(0, 0.5, 0, 0.5)
CURSOR_HOVER_COLOR = Color(1, 0.8, 0, 0.6)
HOVER_COLOR = Color(1, 0.85, 0.1, 0.3)
SELECTED_COLOR = Color(0.1, 0.9, 0.3, 0.35)
HIGHLIGHT_PADDING = 0.03
HIGHLIGHT_HEIGHT = 0.04
GRAB_SNAP_FINE = 0.1  # passo do arrasto com shift, em unidades do mundo


class State:
    def __init__(self, config: Config, window: Window) -> None:
        self.window: Window = window
        self.scene: Scene
        self.config = config
        self.isometric_camera = IsometricCamera()
        self.perspective_camera = PerspectiveCamera()
        self.camera: AnyCamera = self.isometric_camera  # começa na isométrica
        self.cursor = Cursor()
        self.world_grid = Block(
            transform=Transform.at(0, -0.0575, 0),
            color=COLORS["WHITE"],
            grid_enabled=True,
            self_shadow_enabled=False,
        )
        self.selected = 0
        # objeto sob o mouse, objeto escolhido e objeto sendo arrastado
        self.hovered: Optional[Entity] = None
        self.selected_entity: Optional[Entity] = None
        self.grabbed: Optional[Entity] = None
        self.drop_surface = None
        self.fine = False  # shift segurado: precisão e acesso às peças dos grupos
        self.grab_snap = CURSOR_GRID_STEP
        self.grab_plane = 0.0
        self.grab_base_offset = 0.0
        self.grab_anchor = (glm.vec2(), glm.vec2())
        self.hover_box = self._highlight_box(HOVER_COLOR)
        self.select_box = self._highlight_box(SELECTED_COLOR)

    @staticmethod
    def _highlight_box(color: Color) -> Block:
        return Block(color=color, emissive=True, self_shadow_enabled=False)

    @property
    def camera_mode(self) -> CameraType:
        return self.camera.type

    def camera_for(self, camera_type: CameraType) -> AnyCamera:
        if camera_type is CameraType.Isometric:
            return self.isometric_camera
        if camera_type is CameraType.Perspective:
            return self.perspective_camera
        raise ValueError(f"camera sem instância no State: {camera_type}")

    def selected_object(self) -> Optional[Entity]:
        objects = self.scene.objects
        if not objects:
            return None
        return objects[self.selected % len(objects)]

    def update_cursor(self, x: float, y: float) -> None:
        window = self.window
        world = self.isometric_camera.mouse_to_world(
            x,
            y,
            window.width,
            window.height,
            window.framebuffer_width / max(window.framebuffer_height, 1),
        )
        x = (floor(world.x / CURSOR_GRID_STEP) + 0.5) * CURSOR_GRID_STEP
        z = (floor(world.z / CURSOR_GRID_STEP) + 0.5) * CURSOR_GRID_STEP
        self.cursor.move_to(x, 0, z)

    def _walk(self, entities=None, parent=None, matrix=None, skip=None, nested=True):
        """
        Tudo que pode ser pego, como (entity, grupo pai, matriz do pai): os objetos
        soltos na cena e os Groups dentro de Groups (cafeteira no balcão, cadeira
        da mesa...). Peças primitivas (Blocks de dentro de um Group) ficam de fora.
        Com nested=False só os objetos soltos na cena: cada Group conta como um item.
        """
        for entity in self.scene.objects if entities is None else entities:
            if entity is skip:
                continue
            yield entity, parent, matrix
            if nested and isinstance(entity, Group):
                yield from self._walk(
                    [part for part in entity.parts if isinstance(part, Group)],
                    entity,
                    entity.world_matrix(matrix),
                    skip,
                )

    def _locate(self, entity: Entity):
        for found, parent, matrix in self._walk():
            if found is entity:
                return parent, matrix
        return None

    def _ray(self, x: float, y: float):
        window = self.window
        return self.isometric_camera.mouse_ray(
            x,
            y,
            window.width,
            window.height,
            window.framebuffer_width / max(window.framebuffer_height, 1),
        )

    @staticmethod
    def _ground(ray, plane_y: float) -> glm.vec3:
        origin, direction = ray
        return origin + direction * ((plane_y - origin.y) / direction.y)

    @staticmethod
    def _footprint_contains(low: glm.vec3, high: glm.vec3, point: glm.vec3) -> bool:
        return low.x <= point.x <= high.x and low.z <= point.z <= high.z

    def pick(self, x: float, y: float) -> Optional[Entity]:
        """
        Objeto selecionável cujo "pé" (a pegada no plano em que ele está apoiado)
        está sob o cursor. Se várias pegadas se sobrepõem, vence a menor.
        Sem shift pega o grupo inteiro; com shift, também as peças de dentro.
        """
        ray = self._ray(x, y)
        best, best_area = None, float("inf")
        for entity, _, matrix in self._walk(nested=self.fine):
            if not entity.selectable:
                continue
            low, high = entity.bounds(matrix)
            if self._footprint_contains(low, high, self._ground(ray, low.y)):
                area = (high.x - low.x) * (high.z - low.z)
                if area < best_area:
                    best, best_area = entity, area
        return best

    def _surface_under(self, ray, grabbed: Entity):
        """(superfície, topo, matriz do pai) sob o cursor, se for um prop"""
        if not grabbed.prop:
            return None
        best, best_area = None, float("inf")
        for entity, _, matrix in self._walk(skip=grabbed):
            if not entity.surface:
                continue
            low, high = entity.bounds(matrix)
            if self._footprint_contains(low, high, self._ground(ray, high.y)):
                area = (high.x - low.x) * (high.z - low.z)
                if area < best_area:
                    best, best_area = (entity, high.y, matrix), area
        return best

    @staticmethod
    def _yaw(matrix: glm.mat4x4) -> float:
        return glm.degrees(glm.atan(-matrix[0][2], matrix[0][0]))

    def _drag(self, x: float, y: float) -> None:
        grabbed = self.grabbed
        assert grabbed is not None
        ray = self._ray(x, y)
        self.drop_surface = self._surface_under(ray, grabbed)
        plane = self.drop_surface[1] if self.drop_surface else 0.0
        point = self._ground(ray, plane)
        mouse = glm.vec2(point.x, point.z)
        here = glm.vec2(grabbed.get_x(), grabbed.transform.position.z)
        if plane != self.grab_plane:
            # mudou de plano (chão <-> topo do balcão): reancora para não pular
            self.grab_plane = plane
            self.grab_anchor = (mouse, here)
        anchor_mouse, anchor_object = self.grab_anchor
        delta = (mouse - anchor_mouse) / self.grab_snap
        target = anchor_object + glm.vec2(round(delta.x), round(delta.y)) * self.grab_snap
        grabbed.move_to(target.x, plane + self.grab_base_offset, target.y)

    def highlights(self) -> List[Block]:
        """Placas translúcidas no chão sob o objeto selecionado e o sob o mouse"""
        boxes = []
        for box, entity in (
            (self.select_box, self.selected_entity),
            (
                self.hover_box,
                self.hovered if self.hovered is not self.selected_entity else None,
            ),
        ):
            located = self._locate(entity) if entity is not None else None
            if located is None:
                continue
            low, high = entity.bounds(located[1])
            box.move_to(
                (low.x + high.x) / 2, low.y + HIGHLIGHT_HEIGHT / 2, (low.z + high.z) / 2
            )
            box.scale_to(
                high.x - low.x + 2 * HIGHLIGHT_PADDING,
                HIGHLIGHT_HEIGHT,
                high.z - low.z + 2 * HIGHLIGHT_PADDING,
            )
            boxes.append(box)
        return boxes

    def update_world_grid(self, aspect: float) -> None:
        window = self.window
        center = self.isometric_camera.mouse_to_world(
            window.width / 2,
            window.height / 2,
            window.width,
            window.height,
            aspect,
        )
        size = max(
            self.isometric_camera.zoom_level,
            self.isometric_camera.zoom_level * aspect,
        ) * 8
        self.world_grid.move_to(center.x, -0.0575, center.z)
        self.world_grid.scale_to(size, 0.005, size)

    def update(self, dt: float = 0.0) -> None:
        self.isometric_camera.update_rotation(dt)
        if self.camera_mode is CameraType.Isometric:
            x, y = glfw.get_cursor_pos(self.window.inner)
            self.update_cursor(x, y)
            self.fine = any(
                glfw.get_key(self.window.inner, key) == glfw.PRESS
                for key in (glfw.KEY_LEFT_SHIFT, glfw.KEY_RIGHT_SHIFT)
            )
            if self.grabbed is not None:
                self._drag(x, y)
            on_sidebar = x < Sidebar.width
            self.hovered = (
                self.grabbed
                if self.grabbed is not None
                else None if on_sidebar else self.pick(x, y)
            )
            self.cursor.parts[0].color = (
                CURSOR_HOVER_COLOR if self.hovered else CURSOR_COLOR
            )

    @singledispatchmethod
    def handle_event(
        self,
        event: Event,
    ) -> None:

        print("event not handled: ", event)

    @handle_event.register
    def _(self, event: CloseApplication) -> None:
        self.window.close()

    @handle_event.register
    def _(self, event: SpawObject) -> None:
        self.scene.objects.append(event.object)
        self.selected_entity = event.object
        print(f"spawed object {event.object}")

    @handle_event.register
    def _(self, event: RemoveSelectedObject) -> None:
        obj = self.selected_entity
        located = self._locate(obj) if obj is not None else None
        if located is None:
            return
        parent = located[0]
        (self.scene.objects if parent is None else parent.parts).remove(obj)
        self.selected_entity = self.grabbed = self.hovered = None
        print(f"removed object: {obj}")

    @handle_event.register
    def _(self, event: GrabObject) -> None:
        obj = self.selected_entity = self.hovered
        self.grabbed = None
        located = self._locate(obj) if obj is not None else None
        if located is None:
            return
        parent, matrix = located
        low, _ = obj.bounds(matrix)
        if parent is not None:
            # tira do grupo e solta na cena, mantendo posição e giro no mundo
            world = obj.world_matrix(matrix)
            parent.parts.remove(obj)
            obj.transform = Transform(
                position=glm.vec3(world[3]),
                rotation=glm.dvec3(0, self._yaw(world), 0),
                scale=obj.transform.scale,
            )
            self.scene.objects.append(obj)
        self.grabbed = obj
        self.grab_snap = GRAB_SNAP_FINE if self.fine else CURSOR_GRID_STEP
        self.drop_surface = None
        self.grab_plane = low.y
        self.grab_base_offset = obj.get_y() - low.y
        x, y = glfw.get_cursor_pos(self.window.inner)
        point = self._ground(self._ray(x, y), low.y)
        self.grab_anchor = (
            glm.vec2(point.x, point.z),
            glm.vec2(obj.get_x(), obj.transform.position.z),
        )

    @handle_event.register
    def _(self, event: ReleaseObject) -> None:
        obj, self.grabbed = self.grabbed, None
        surface, self.drop_surface = self.drop_surface, None
        if obj is None or surface is None:
            return
        # props soltos sobre uma superfície passam a fazer parte dela
        parent, _, matrix = surface
        local = glm.inverse(parent.world_matrix(matrix)) * obj.model
        self.scene.objects.remove(obj)
        obj.transform = Transform(
            position=glm.vec3(local[3]),
            rotation=glm.dvec3(0, self._yaw(local), 0),
            scale=obj.transform.scale,
        )
        parent.parts.append(obj)

    @handle_event.register
    def _(self, event: ToggleNight) -> None:
        toggle = getattr(self.scene, "toggle_night", None)
        if toggle is not None:
            toggle()

    @handle_event.register
    def _(self, event: InteractWithSelectedObject) -> None:
        toggle = getattr(self.selected_entity, "toggle", None)
        if toggle is not None:
            toggle()

    @handle_event.register
    def _(self, event: RotateSelectedObject) -> None:
        obj = self.selected_entity
        if obj is not None:
            rotation = obj.transform.rotation
            obj.rotate_to(rotation.x, (rotation.y + event.degrees) % 360, rotation.z)

    @handle_event.register
    def _(self, event: SelectNextObject) -> None:
        if self.scene.objects:
            self.selected = (self.selected + 1) % len(self.scene.objects)

    @handle_event.register
    def _(self, event: MoveSelectedObject) -> None:
        obj = self.selected_object()
        if obj is not None:
            obj.move_by(event.dx, event.dy, event.dz)

    @handle_event.register
    def _(self, event: ChangeCameraRequest) -> None:

        # rotaciona para o próximo tipo de camera disponível
        self.camera = self.camera_for(self.camera_mode.next())
        print(f"change camera type to: {self.camera.type}")
        cursor_type = (
            glfw.CURSOR_DISABLED
            if isinstance(self.camera, PerspectiveCamera)
            else glfw.CURSOR_NORMAL
        )
        glfw.set_input_mode(self.window.inner, glfw.CURSOR, cursor_type)

    @handle_event.register
    def _(self, event: MoveCamera) -> None:
        # as duas câmeras andam com WASD, cada uma do seu jeito
        self.camera.move(event.forward, event.strafe, event.dt)

    @handle_event.register
    def _(self, event: RotateCamera) -> None:
        camera = self.camera
        if isinstance(camera, PerspectiveCamera):
            camera.rotate(event.dx, event.dy)

    @handle_event.register
    def _(self, event: RotateIsometricCamera) -> None:
        direction = 1 if event.direction is IsometricRotationDirection.Left else -1
        self.isometric_camera.rotate_quarter_turn(direction)

    @handle_event.register
    def _(self, event: UpdateZoomLevel) -> None:
        camera = self.camera
        if isinstance(camera, IsometricCamera):
            camera.set_zoom(camera.zoom_level + event.amount)

    def start(self) -> None:
        self.scene = CoffeeShopScene()
        self.isometric_camera.set_zoom(self.scene.iso_zoom)
        print(f"{len(self.scene.objects)} objetos na aplicação")
