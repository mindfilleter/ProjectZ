import pygame
from pygame import display
from pygame import time

from projectz import title
from projectz.core import game


def init_pygame() -> None:
    pygame.init()
    display.set_mode((800, 600))
    display.set_caption("ProjectZ")


def create_game() -> game.Game:
    g = game.Game(time.Clock())

    title_scene = title.TitleScene()
    g[title_scene.name] = title_scene
    g.set_current_scene(title.TitleScene)

    return g
