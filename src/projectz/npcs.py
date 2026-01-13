from importlib import resources
from pygame import sprite
from pygame import math
import pygame
import random

from projectz.animated_sprite import AnimatedSprite
from projectz.common import Collidable, Pathfinder


class NPC(AnimatedSprite):
    def __init__(self, spritesheet_path, x: float, y: float, *groups):
        super().__init__(spritesheet_path, *groups)
        self.dialogs = []
        self.position = math.Vector2(x, y)

    def cycle_dialogs(self):
        if self.dialogs:
            self.dialogs.insert(0, self.dialogs.pop())

    @property
    def dialog(self) -> str:
        return self.dialogs[-1]


WANDERING_NPC_ANIMATION_LAYOUT = {
    "idle_down": {"frames": [{"x": 0, "y": 0}], "speed": 1},
    "idle_up": {"frames": [{"x": 1, "y": 1}], "speed": 1},
    "idle_right": {"frames": [{"x": 1, "y": 0}], "speed": 1},
    "idle_left": {"frames": [{"x": 0, "y": 1}], "speed": 1},
    "walk_down": {
        "frames": [{"x": 0, "y": 0}],
        "speed": 1,
    },
    "walk_up": {
        "frames": [{"x": 1, "y": 1}],
        "speed": 1,
    },
    "walk_right": {
        "frames": [{"x": 1, "y": 0}],
        "speed": 1,
    },
    "walk_left": {
        "frames": [{"x": 0, "y": 1}],
        "speed": 1,
    },
}


class WanderingNPC(NPC):
    def __init__(self, game, spawn, boundaries: pygame.Rect, *groups) -> None:
        super().__init__("wandering_npc.png", spawn.x, spawn.y, *groups)

        self.rect = self.image.get_rect(topleft=(spawn.x, spawn.y))

        self.boundaries = boundaries
        self.pathfinder = Pathfinder(game, spawn.x, spawn.y, self)
        self.collidable = Collidable(game, spawn.x, spawn.y, self)

        self.pos = math.Vector2(spawn.x, spawn.y)
        self.target = None
        self.spd = 0.5
        self.path_timer = 0
        self.path_timeout = 3000  # 3 seconds
        self.path = []
        self.facing = "down"

        dialog_keys = sorted(
            [key for key in spawn.properties if key.startswith("dialog_")]
        )
        for key in dialog_keys:
            self.dialogs.append(spawn.properties[key])

    def update(self, dt, collision_rects):
        is_moving = False
        # If the path is empty or timed out, find a new target
        if not self.path and (
            self.target is None
            or pygame.time.get_ticks() - self.path_timer > self.path_timeout
        ):
            self.target = self.find_new_target()
            if self.target:
                self.path = self.pathfinder.get_path(
                    self.rect.center, self.target
                )
                self.path_timer = pygame.time.get_ticks()

        # If we have a path, move along it
        if self.path:
            is_moving = True
            next_point = pygame.math.Vector2(self.path[0])
            direction = next_point - self.pos

            # If we are close enough to the next point, move to the next one
            if direction.length() < 2:  # A small threshold
                self.path.pop(0)
                if (
                    not self.path
                ):  # If path is now empty, we've reached the destination
                    self.target = None
                    return
                else:
                    next_point = pygame.math.Vector2(self.path[0])
                    direction = next_point - self.pos

            if direction.length() > 0:
                direction.normalize_ip()
            if abs(direction.x) > abs(direction.y):
                if direction.x > 0:
                    self.facing = "right"
                else:
                    self.facing = "left"
            else:
                if direction.y > 0:
                    self.facing = "down"
                else:
                    self.facing = "up"

            movement = direction * self.spd

            # Move and slide along walls
            new_pos = self.pos + movement

            # Move on X axis
            if not self.collidable.check_collision(dx=movement.x):
                self.pos.x = new_pos.x

            # Move on Y axis
            if not self.collidable.check_collision(dy=movement.y):
                self.pos.y = new_pos.y

            self.rect.center = self.pos

        # --- Animation ---
        if is_moving:
            self.state = f"walk_{self.facing}"
        else:
            self.state = f"idle_{self.facing}"
        self.update_animation(dt)

    def find_new_target(self):
        tile_size = self.collidable.game.TILE_SIZE
        attempts = 0
        while attempts < 20:  # Try up to 20 times to find a valid spot
            rand_x = random.randint(
                self.boundaries.left, self.boundaries.right - tile_size
            )
            rand_y = random.randint(
                self.boundaries.top, self.boundaries.bottom - tile_size
            )

            # Align to tile grid and get center
            target_x = (rand_x // tile_size) * tile_size + (tile_size // 2)
            target_y = (rand_y // tile_size) * tile_size + (tile_size // 2)

            # Create a rect for the target tile
            target_rect = pygame.Rect(
                target_x - tile_size // 2,
                target_y - tile_size // 2,
                tile_size,
                tile_size,
            )

            # Ensure the target is within the wandering boundaries and not in a wall
            if self.boundaries.contains(
                target_rect
            ) and not self.collidable.game.map.is_wall(target_x, target_y):
                return pygame.math.Vector2(target_x, target_y)
            attempts += 1
        return None  # Return None if no valid target found
