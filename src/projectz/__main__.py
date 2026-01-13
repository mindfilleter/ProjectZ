"""
This module contains the main entry point for the game.
"""
from projectz.logger import logger
import pygame

from projectz.bootstrap import init_pygame
from projectz import game
from projectz import config


def main():
    """
    The main entry point for the game.
    """
    logger.info("Starting ProjectZ...")
    init_pygame()

    g = game.Game(config.get_config())
    g.start()
    pygame.quit()


if __name__ == "__main__":
    main()
