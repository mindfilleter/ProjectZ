import logging

import pygame
from pygame import display
from pygame import event
from pygame import sprite

from projectz import assets
from projectz.core import entity
from projectz.core import errors
from projectz.core import scene
from projectz.ui import button

logger = logging.getLogger(__name__)


class TitleScene(scene.Scene):
    def __init__(self) -> None:
        self.sprites: sprite.Group[entity.Entity] = sprite.Group()
        bg = entity.Entity(self.sprites)
        bg.image = assets.get_image("title-bg.png")
        bg.rect = pygame.Rect((0, 0), bg.image.get_size())
        logger.debug(bg.rect)

        screen = display.get_surface()
        if not screen:
            raise RuntimeError("No display surface found")
        screen_rect = screen.get_rect()

        button_size = (200, 50)
        button_margin = 10
        grid_width = 2 * button_size[0] + button_margin
        grid_height = 2 * button_size[1] + button_margin

        start_x = screen_rect.centerx - grid_width // 2
        start_y = screen_rect.bottom - grid_height - 50

        # Create and position buttons
        new_game_btn = button.create_button(
            size=button_size,
            text="New Game",
            button_id="new_game",
            normal_color=pygame.Color("darkgreen"),
            hover_color=pygame.Color("green"),
            clicked_color=pygame.Color("lightgreen"),
        )
        if new_game_btn.rect:
            new_game_btn.rect.topleft = (start_x, start_y)
        self.sprites.add(new_game_btn)

        load_game_btn = button.create_button(
            size=button_size,
            text="Load Game",
            button_id="load_game",
            normal_color=pygame.Color("darkblue"),
            hover_color=pygame.Color("blue"),
            clicked_color=pygame.Color("lightblue"),
        )
        if load_game_btn.rect:
            load_game_btn.rect.topleft = (start_x + button_size[0] + button_margin, start_y)
        self.sprites.add(load_game_btn)

        options_btn = button.create_button(
            size=button_size,
            text="Options",
            button_id="options",
            normal_color=pygame.Color("darkgoldenrod"),
            hover_color=pygame.Color("goldenrod"),
            clicked_color=pygame.Color("yellow"),
        )
        if options_btn.rect:
            options_btn.rect.topleft = (start_x, start_y + button_size[1] + button_margin)
        self.sprites.add(options_btn)

        quit_btn = button.create_button(
            size=button_size,
            text="Quit",
            button_id="quit",
            normal_color=pygame.Color("darkred"),
            hover_color=pygame.Color("red"),
            clicked_color=pygame.Color("salmon"),
        )
        if quit_btn.rect:
            quit_btn.rect.topleft = (
                start_x + button_size[0] + button_margin,
                start_y + button_size[1] + button_margin,
            )
        self.sprites.add(quit_btn)

    name = "title"

    def update(self, dt: int) -> None:
        self.sprites.update(dt)

    def draw(self) -> None:
        surface = display.get_surface()
        if surface is None:
            return
        surface.fill(pygame.Color(0, 0, 0))
        self.sprites.draw(surface)
        display.flip()

    def handle_event(self, e: event.Event) -> None:
        for s in self.sprites:
            s.handle_event(e)

        if e.type == pygame.QUIT:
            raise errors.GameExitError("Exiting from title")
        elif e.type == button.BUTTON_CLICKED:
            if e.button_id == "new_game":
                logger.info("New Game button clicked")
            elif e.button_id == "load_game":
                logger.info("Load Game button clicked")
            elif e.button_id == "options":
                logger.info("Options button clicked")
            elif e.button_id == "quit":
                raise errors.GameExitError("Exiting from title via quit button")
