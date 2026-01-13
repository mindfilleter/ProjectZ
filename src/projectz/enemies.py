import math
import random
import pygame
from importlib import resources
from pygame import sprite

from projectz.animated_sprite import AnimatedSprite
from projectz.common import Collidable, Pathfinder


class Enemy(AnimatedSprite):
    def __init__(self, game, x, y, type, player):
        # 1. Initialize the base Sprite class
        super().__init__("slimes.png")

        # Use floating point numbers for smooth movement
        self.pos = pygame.math.Vector2(x, y)
        self.type = type
        self.spd = 0.8 # Slower than player

        # 3. The 'rect' is used for positioning and collision checking.
        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        self.hurtbox = self.rect.copy()

        self.player = player  # Store the player so we can chase them
        self.collidable = Collidable(game, self.pos.x, self.pos.y, self)
        self.pathfinder = Pathfinder(game, self.pos.x, self.pos.y, self)
        self.path = []

    def __repr__(self):
        return f"<Enemy type={self.type} pos={self.pos}>"

    def update(self, dt, collision_rects):
        # Get a new path to the player periodically
        if not self.path or random.randint(0, 100) < 2:  # 2% chance to recalculate path
            self.path = self.pathfinder.get_path(
                self.rect.topleft, self.player.rect.topleft
            )

        is_moving = False
        if self.path:
            is_moving = True
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

            if abs(direction.x) > abs(direction.y):
                if direction.x > 0:
                    self.state = "walk_right"
                else:
                    self.state = "walk_left"
            else:
                if direction.y > 0:
                    self.state = "walk_down"
                else:
                    self.state = "walk_up"

            movement = direction * self.spd

            if not self.collidable.check_collision(dx=movement.x, dy=movement.y):
                self.pos += movement
                self.rect.topleft = self.pos
        if not is_moving:
            self.state = "idle_down"

        self.hurtbox.topleft = self.rect.topleft
        self.update_animation(dt)
        super().update(dt)
