from src.game import Game
from src.texture import ensure_textures


def main():
    ensure_textures()
    Game().run()


if __name__ == "__main__":
    main()
