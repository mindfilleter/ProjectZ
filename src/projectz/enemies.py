import math
import random
import pygame
from importlib import resources
from pygame import sprite

from projectz.common import Collidable, Pathfinder


class Enemy(sprite.Sprite):
    def __init__(self, game, x, y, type, player):
        # 1. Initialize the base Sprite class
        super().__init__()

        # 2. Set the 'Costume' (the image) for the sprite.
        try:
            with resources.path("projectz.assets", "slimes.png") as sheet_path:
                spritesheet = pygame.image.load(sheet_path).convert_alpha()
        except FileNotFoundError:
            print("Error: slimes.png not found. Using red square placeholder.")
            spritesheet = pygame.Surface((16, 16), pygame.SRCALPHA)
            spritesheet.fill((200, 50, 50))

        # Define slime positions on the spritesheet
        slime_positions = {
            "red": (0, 0),  # x, y of the first frame
            "blue": (0, 16),
            "green": (0, 32),
        }

        # Default to red if type is unknown
        slime_type_key = type.split(" ")[0]  # in case of "red slime"
        if slime_type_key not in slime_positions:
            slime_type_key = "red"

        start_x, start_y = slime_positions[slime_type_key]

        # For now, we only use the first frame of the animation
        frame_rect = pygame.Rect(start_x, start_y, 16, 16)
        self.image = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
        self.image.blit(spritesheet, (0, 0), frame_rect)

        # Use floating point numbers for smooth movement
        self.pos = pygame.math.Vector2(x, y)
        self.type = type
        self.spd = 0.8 # Slower than player

        # 3. The 'rect' is used for positioning and collision checking.
        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

        self.player = player  # Store the player so we can chase them
        self.collidable = Collidable(game, self.pos.x, self.pos.y, self)
        self.pathfinder = Pathfinder(game, self.pos.x, self.pos.y, self)
        self.path = []

    def update(self, collision_rects):
        # Get a new path to the player periodically
        if not self.path or random.randint(0, 100) < 2: # 2% chance to recalculate path
             self.path = self.pathfinder.get_path(self.rect.center, self.player.rect.center)
        
        if self.path:
            next_point = pygame.math.Vector2(self.path[0])
            direction = next_point - self.pos

            if direction.length() < 2:
                self.path.pop(0)
                if not self.path:
                    return
                else:
                    next_point = pygame.math.Vector2(self.path[0])
                    direction = next_point - self.pos
            
            if direction.length() > 0:
                direction.normalize_ip()

            movement = direction * self.spd

            if not self.collidable.check_collision(dx=movement.x, dy=movement.y):
                self.pos += movement
                self.rect.center = self.pos
