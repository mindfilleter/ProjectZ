import pygame
from pygame import sprite
from importlib import resources
import pygame.math


class NPC(sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.dialog = []
        self.behavior = "idle"
        try:
            with resources.path("projectz.assets", "wandering_npc.png") as image_path:
                self.image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print("Error: wandering_npc.png not found. Using green square placeholder.")
            self.image = pygame.Surface((16, 16)).convert_alpha()
            self.image.fill((0, 255, 150))
        self.pos = pygame.math.Vector2(400, 300)
        self.vel = pygame.math.Vector2(0, 0)
        self.current_talk = 1
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y)
