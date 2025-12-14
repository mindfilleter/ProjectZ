import math
import pygame
from importlib import resources
from pygame import sprite


class Enemy(sprite.Sprite):
    def __init__(self, x, y, type, player):
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
        self.x = float(x)
        self.y = float(y)
        self.type = type
        self.dir = 0
        self.spd = 5
        self.friction = 5

        # 3. The 'rect' is used for positioning and collision checking.
        self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))

        self.player = player  # Store the player so we can chase them

    def update(self, collision_rects):

        # Calculate the distance and direction to the player
        # We target the player's center for smooth tracking

        if self.spd <= 0.01:
            self.spd = 2
            self.dx = (
                self.player.rect.centerx - self.x
            )  # Calculate difference (Player - Enemy)
            self.dy = (
                self.player.rect.centery - self.y
            )  # Calculate difference (Player - Enemy)

            # Calculate the angle (in radians) to the player
            self.dir = math.atan2(self.dy, self.dx)
        else:
            self.spd -= 0.05

        # Calculate new position based on speed and direction
        new_x = self.x + math.cos(self.dir) * self.spd
        new_y = self.y + math.sin(self.dir) * self.spd

        # Store old position for collision rollback
        prev_x = self.x
        prev_y = self.y

        # --- Collision Check (Horizontal) ---
        self.x = new_x
        self.rect.x = int(self.x)

        # Check if the new X position hits a wall
        for wall in collision_rects:
            if self.rect.colliderect(wall):
                self.x = prev_x  # If it hits, move back
                self.rect.x = int(self.x)
                break  # Stop checking walls

        # --- Collision Check (Vertical) ---
        self.y = new_y
        self.rect.y = int(self.y)

        # Check if the new Y position hits a wall
        for wall in collision_rects:
            if self.rect.colliderect(wall):
                self.y = prev_y  # If it hits, move back
                self.rect.y = int(self.y)
                break  # Stop checking walls
