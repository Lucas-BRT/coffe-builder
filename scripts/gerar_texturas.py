"""
Gera as texturas procedurais em assets/textures. Todas são em tons de cinza claro
e sem emenda (repetem sem costura): a cor do objeto é multiplicada pela textura no
shader, então o objeto mantém a cor e ganha o relevo.

uso: python scripts/gerar_texturas.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "textures"
SIZE = 256
rng = np.random.default_rng(7)


def noise(cells_x: int, cells_y: int = 0) -> np.ndarray:
    """
    Ruído suave que repete nas bordas (filtro passa-baixa por FFT), de 0 a 1.
    cells_x/cells_y: quantas "manchas" cabem em cada eixo (mais células, mais fino)
    """
    cells_y = cells_y or cells_x
    fx = np.fft.fftfreq(SIZE)[None, :] * SIZE
    fy = np.fft.fftfreq(SIZE)[:, None] * SIZE
    spectrum = np.fft.fft2(rng.random((SIZE, SIZE))) * np.exp(
        -2 * ((fx / cells_x) ** 2 + (fy / cells_y) ** 2)
    )
    low = np.real(np.fft.ifft2(spectrum))
    return (low - low.min()) / (low.max() - low.min())


def save(name: str, values: np.ndarray) -> None:
    gray = (np.clip(values, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(np.stack([gray] * 3, axis=-1)).save(OUT / name)


y, x = np.mgrid[0:SIZE, 0:SIZE] / SIZE
TAU = 2 * np.pi

# reboco: manchas suaves e grão fino
save("reboco.png", 0.88 + 0.08 * noise(12) + 0.04 * rng.random((SIZE, SIZE)))

# tecido: trama de fios cruzados
weave = np.sin(TAU * x * 48) * np.sin(TAU * y * 48)
save("tecido.png", 0.82 + 0.1 * weave + 0.06 * noise(10))

# madeira clara: veios ao longo do eixo X, com ondulação
rings = np.sin(TAU * (y * 10 + noise(2, 3) * 2.5))
streaks = noise(3, 90)  # fibras finas ao longo do eixo X
save("madeira_clara.png", 0.82 + 0.1 * rings + 0.1 * streaks)

# mármore: quase branco, com veios largos e bem suaves (sem linhas marcadas)
veins = np.abs(np.sin(TAU * (x * 1 + y * 2 + noise(4) * 1.2)))
save("marmore.png", 0.97 - 0.05 * (1 - veins) ** 3 - 0.03 * noise(6) + 0.02 * noise(24))
