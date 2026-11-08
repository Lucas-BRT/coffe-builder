from __future__ import annotations

from ctypes import c_void_p
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from OpenGL.GL import *

from src.objects import COLORS, Color, Entity
from src.objects.armchair import Armchair
from src.objects.cafe_chair import CafeChair
from src.objects.chair import Chair
from src.objects.coffee_machine import CoffeeMachine
from src.objects.coffee_table import CoffeeTable
from src.objects.components import Block
from src.objects.counter import Counter
from src.objects.cup import Cup
from src.objects.floor_lamp import FloorLamp
from src.objects.L_counter import LCounter
from src.objects.menu import Menu
from src.objects.round_table import RoundTable
from src.objects.table import Table

SHADERS_DIR = Path(__file__).resolve().parent.parent / "shaders"

FONT = {
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("011", "100", "100", "100", "011"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("011", "100", "101", "101", "011"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "010"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("010", "101", "101", "101", "010"),
    "P": ("110", "101", "110", "100", "100"),
    "Q": ("010", "101", "101", "110", "011"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
}


@dataclass(frozen=True)
class SidebarItem:
    name: str
    create: Callable[[], Entity]
    color: Color


class Sidebar:
    width = 180
    row_top = 58
    row_height = 54
    row_gap = 8

    def __init__(self) -> None:
        self.items = [
            SidebarItem("CHAIR", Chair, COLORS["LIGHT_BROWN"]),
            SidebarItem("TABLE", Table, COLORS["BROWN"]),
            SidebarItem("COUNTER", Counter, COLORS["RED"]),
            SidebarItem("BLOCK", Block.cube, COLORS["BLUE"]),
            SidebarItem("CAFE CHAIR", CafeChair, COLORS["LIGHT_BROWN"]),
            SidebarItem("ARMCHAIR", Armchair, COLORS["ORANGE"]),
            SidebarItem("ROUND TBL", RoundTable, COLORS["BROWN"]),
            SidebarItem("COFFEE TBL", CoffeeTable, COLORS["BROWN"]),
            SidebarItem("L COUNTER", LCounter, COLORS["RED"]),
            SidebarItem("ESPRESSO", CoffeeMachine, COLORS["DARK_GRAY"]),
            SidebarItem("CUP", Cup, COLORS["LIGHT_GRAY"]),
            SidebarItem("LAMP", FloorLamp, COLORS["YELLOW"]),
            SidebarItem("MENU", Menu, COLORS["GREEN"]),
        ]
        self.scroll = 0.0
        self.dragging: Optional[SidebarItem] = None
        self.shader = self._create_program("sidebar.vert", "sidebar.frag")
        self.viewport_uniform = glGetUniformLocation(self.shader, "viewport_size")
        self.vao = int(glGenVertexArrays(1))
        self.vbo = int(glGenBuffers(1))
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        stride = 5 * np.dtype(np.float32).itemsize
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, c_void_p(8))
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)

    footer = 44

    def scroll_by(self, amount: float, height: int) -> None:
        pitch = self.row_height + self.row_gap
        visible = height - self.row_top - self.footer
        max_scroll = max(0, len(self.items) * pitch - visible)
        self.scroll = min(max(self.scroll + amount, 0), max_scroll)

    def item_at(self, x: float, y: float) -> Optional[SidebarItem]:
        if x < 0 or x >= self.width or y < self.row_top:
            return None
        for index, item in enumerate(self.items):
            top = self.row_top + index * (self.row_height + self.row_gap) - self.scroll
            if top <= y < top + self.row_height:
                return item
        return None

    def render(self, width: int, height: int, polygon_mode: int) -> None:
        vertices = []

        def rect(x: float, y: float, w: float, h: float, color) -> None:
            r, g, b = color
            for px, py in (
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y),
                (x + w, y + h),
                (x, y + h),
            ):
                vertices.extend((px, py, r, g, b))

        def text(value: str, x: int, y: int, scale: int, color) -> None:
            cursor_x = x
            for char in value:
                glyph = FONT.get(char)
                if glyph:
                    for row, bits in enumerate(glyph):
                        for column, bit in enumerate(bits):
                            if bit == "1":
                                rect(
                                    cursor_x + column * scale,
                                    y + row * scale,
                                    scale,
                                    scale,
                                    color,
                                )
                cursor_x += 4 * scale

        rect(0, 0, self.width, height, (0.09, 0.10, 0.12))
        rect(self.width - 1, 0, 1, height, (0.24, 0.26, 0.29))
        for index, item in enumerate(self.items):
            top = self.row_top + index * (self.row_height + self.row_gap) - self.scroll
            if top + self.row_height < self.row_top or top > height - self.footer:
                continue
            selected = item is self.dragging
            rect(
                10,
                top,
                self.width - 20,
                self.row_height,
                (0.20, 0.22, 0.25)
                if selected
                else (0.13, 0.15, 0.17),
            )
            rect(20, top + 15, 24, 24, (item.color.r, item.color.g, item.color.b))
            text(item.name, 58, top + 20, 3, (0.91, 0.92, 0.94))
        # cobre as linhas que passam por baixo do título e do rodapé
        panel = (0.09, 0.10, 0.12)
        rect(0, 0, self.width - 1, self.row_top, panel)
        rect(0, height - self.footer, self.width - 1, self.footer, panel)
        text("OBJECTS", 20, 20, 3, (0.94, 0.95, 0.97))
        text("DRAG TO WORLD", 18, height - 32, 2, (0.57, 0.61, 0.65))

        data = np.asarray(vertices, dtype=np.float32)
        glDisable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glUseProgram(self.shader)
        glUniform2f(self.viewport_uniform, width, height)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
        glDrawArrays(GL_TRIANGLES, 0, len(data) // 5)
        glBindVertexArray(0)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, polygon_mode)

    @staticmethod
    def _create_program(vertex_file: str, fragment_file: str) -> int:
        def compile_shader(shader_type: int, filename: str) -> int:
            shader = glCreateShader(shader_type)
            glShaderSource(shader, (SHADERS_DIR / filename).read_text())
            glCompileShader(shader)
            if not glGetShaderiv(shader, GL_COMPILE_STATUS):
                raise RuntimeError(glGetShaderInfoLog(shader).decode())
            return shader

        vertex = compile_shader(GL_VERTEX_SHADER, vertex_file)
        fragment = compile_shader(GL_FRAGMENT_SHADER, fragment_file)
        program = glCreateProgram()
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(program).decode())
        glDeleteShader(vertex)
        glDeleteShader(fragment)
        return program
