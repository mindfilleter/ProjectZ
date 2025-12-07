from pygame import display
from pygame import event
from pygame import time

import pygame

from projectz import map


class Game:

    TARGET_FPS = 60

    def __init__(self, config):
        self.config = config
        self.clock = time.Clock()
        self.running = True
        

    def start(self):
        tiled_map = map.load_map("map.tmx")
        screen = display.get_surface()
        while self.running:
            self.clock.tick(Game.TARGET_FPS)
            
            for pygame_event in event.get():
                if pygame_event.type == pygame.QUIT:
                    self.running = False

            screen.fill((0, 0, 0))
            map.render_map(screen, tiled_map)
            pygame.display.flip()
