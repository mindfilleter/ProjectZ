import pygame

from projectz import bootstrap
from projectz.core import log_config

if __name__ == "__main__":
    clock = pygame.time.Clock()
    bootstrap.init_pygame()

    g = bootstrap.create_game(clock)
    log_config.setup_logging(clock, g)
    g.main_loop()
    pygame.quit()
