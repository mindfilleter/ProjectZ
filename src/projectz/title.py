import logging

import pygame
from pygame import display
from pygame import event
from pygame import sprite

from projectz import assets
from projectz.core import entity
from projectz.core import errors
from projectz.core import scene

logger = logging.getLogger(__name__)


class TitleScene(scene.Scene):
    def __init__(self) -> None:
        self.sprites: sprite.Group[entity.Entity] = sprite.Group()
        bg = entity.Entity(self.sprites)
        bg.image = assets.get_image("title-bg.png")
        bg.rect = pygame.Rect((0, 0), bg.image.get_size())
        logger.debug(bg.rect)

    name = "title"

    def update(self, dt: int) -> None:
        pass

    def draw(self) -> None:
        surface = display.get_surface()
        if surface is None:
            return
        surface.fill(0)
        self.sprites.draw(surface)
        display.flip()

    def handle_event(self, e: event.Event) -> None:
        if e.type == pygame.QUIT:
            raise errors.GameExitError("Exiting from title")
