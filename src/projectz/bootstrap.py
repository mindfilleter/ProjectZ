import pygame

from projectz.config import config


def init_pygame():
    """Initializes Pygame and sets up the display."""
    pygame.init()

    # Get screen dimensions from config
    screen_width = config.getint("screen", "width")
    screen_height = config.getint("screen", "height")
    fullscreen = config.getboolean("screen", "fullscreen")

    # Set display mode
    if fullscreen:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("Project Z")

    return screen
