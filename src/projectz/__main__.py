import logging

import pygame

from projectz import bootstrap

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bootstrap.init_pygame()
    g = bootstrap.create_game()
    g.main_loop()
    pygame.quit()
