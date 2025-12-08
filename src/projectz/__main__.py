import pygame

from projectz.bootstrap import init_pygame
from projectz import game
from projectz import config


def main():
    """The main entry point for the game."""
    screen = init_pygame()

    g = game.Game(config.get_config())
    g.start()
    pygame.quit()


if __name__ == "__main__":
    main()


class Player(sprite.Sprite):

    def __init__(self, *groups):
        sprite.Sprite.__init__(self, *groups)
