import pygame
from pygame import sprite
from importlib import resources
import pygame.math


class NPC(sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.spritesheet = None
        self.dialog = []
        self.behavior = "idle"
        self.image = pygame.Surface((16, 16)).convert_alpha()
        self.image.fill(0, 255, 150)
        self.pos = pygame.math.Vector2(400, 300)
        self.vel = pygame.math.Vector2(0, 0)
        self.current_talk = 1
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y)
