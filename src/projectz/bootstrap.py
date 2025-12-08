"""
This module contains the initialization logic for Pygame.
"""

import pygame

from projectz.config import config


def init_pygame():
    """
    Initializes Pygame and sets up the display.

    Returns:
        The screen surface.
    """
    pygame.init()

    screen_width = config.getint("screen", "width")
    screen_height = config.getint("screen", "height")
    fullscreen = config.getboolean("screen", "fullscreen")

    if fullscreen:
        screen = pygame.display.set_mode(
            (screen_width, screen_height), pygame.FULLSCREEN
        )
    else:
        screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("Project Z")

    return screen
