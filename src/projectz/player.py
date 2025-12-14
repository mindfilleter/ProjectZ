import pygame
from pygame import sprite
from pygame import rect
from importlib import resources
import pygame.math


class Player(sprite.Sprite):
    """
    Represents the player character.
    """

    def __init__(self, tile_size, *groups):
        """
        Initializes the player.

        Args:
            *groups: The sprite groups to add the player to.
        """
        super().__init__(*groups)
        # Using Vector2 for smooth floating point positioning
        self.pos = pygame.math.Vector2(tile_size, tile_size)
        self.vel = pygame.math.Vector2(0, 0)
        self.spd = 1
        self.friction = 0.7
        self.hit_point_max = 4
        self._hit_points = self.hit_point_max
        # Rect for drawing and collision (must be integer coordinates)
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y, tile_size, tile_size)
        self.move_dir = []

        try:
            with resources.path("projectz.assets", "player.png") as sheet_path:
                spritesheet = pygame.image.load(sheet_path).convert_alpha()
        except FileNotFoundError:
            print("Error: player.png not found. Using red square placeholder.")
            spritesheet = pygame.Surface((32, 32), pygame.SRCALPHA)
            spritesheet.fill((255, 0, 0))

        # Example frame at 32, 0, assuming 16x16 tiles
        frame_rect = pygame.Rect(32, 0, tile_size, tile_size)

        self.image = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
        self.image.blit(spritesheet, (0, 0), frame_rect)

    @property
    def hit_points(self):
        return self._hit_points

    @hit_points.setter
    def hit_points(self, value):
        self._hit_points = max(0, min(value, self.hit_point_max))

    KEY_DIRECTION_MAP = {
        pygame.K_d: "right",
        pygame.K_a: "left",
        pygame.K_w: "up",
        pygame.K_s: "down",
    }

    def handle_event(self, pygame_event):
        """
        Handles a pygame event.

        Args:
            pygame_event: The event to handle.
        """
        if pygame_event.type not in (pygame.KEYDOWN, pygame.KEYUP):
            return

        direction = self.KEY_DIRECTION_MAP.get(pygame_event.key)
        if not direction:
            return

        if pygame_event.type == pygame.KEYDOWN:
            if direction not in self.move_dir:
                self.move_dir.append(direction)
        elif pygame_event.type == pygame.KEYUP:
            if direction in self.move_dir:
                self.move_dir.remove(direction)

    def update(self, collision_rects):
        """
        Updates the player's state and handles collision.

        Args:
            collision_rects: A list of rects to check for collisions.
        """
        # Input processing
        if "right" in self.move_dir:
            self.vel.x += self.spd
        if "left" in self.move_dir:
            self.vel.x -= self.spd
        if "up" in self.move_dir:
            self.vel.y -= self.spd
        if "down" in self.move_dir:
            self.vel.y += self.spd

        # Apply friction
        self.vel *= self.friction

        # --- Horizontal Movement and Collision ---
        prev_pos_x = self.pos.x
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)

        for wall in collision_rects:
            if self.rect.colliderect(wall):
                # Rollback X position
                self.pos.x = prev_pos_x
                self.rect.x = int(self.pos.x)
                self.vel.x = 0
                break  # Only need to rollback once

        # --- Vertical Movement and Collision ---
        prev_pos_y = self.pos.y
        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)

        for wall in collision_rects:
            if self.rect.colliderect(wall):
                # Rollback Y position
                self.pos.y = prev_pos_y
                self.rect.y = int(self.pos.y)
                self.vel.y = 0
                break