import pygame
from typing import Set
import pygame.math
import enum

from projectz.animated_sprite import AnimatedSprite
from projectz.common import Collidable


class KeyItems(enum.Enum):
    Sword = "Sword"


class Player(AnimatedSprite):
    """
    Represents the player character.
    """

    def __init__(self, game, tile_size, *groups):
        """
        Initializes the player.

        Args:
            *groups: The sprite groups to add the player to.
        """
        super().__init__("player.png", max_hp=4, *groups)
        # Using Vector2 for smooth floating point positioning
        self.pos = pygame.math.Vector2(tile_size, tile_size)
        self.vel = pygame.math.Vector2(0, 0)
        self.spd = 1
        self.friction = 0.7
        # Rect for drawing and collision (must be integer coordinates)
        self.rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
        self.move_dir = []
        self.inventory: Set[KeyItems] = set([])
        self.collidable = Collidable(game, self.pos.x, self.pos.y, self)
        self.facing = "down"
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 200  # ms
        self.hitbox = None

    def give_item(self, key_item: KeyItems):
        self.inventory.add(key_item)

    def attack(self, enemy_group):
        if not self.attacking:
            self.attacking = True
            self.attack_timer = pygame.time.get_ticks()
            self.state = f"attack_{self.facing}"

            # Create hitbox based on facing direction
            hitbox_size = (self.rect.width, self.rect.height)
            hitbox_pos = list(self.rect.topleft)

            if self.facing == "right":
                hitbox_pos[0] += self.rect.width
            elif self.facing == "left":
                hitbox_pos[0] -= self.rect.width
            elif self.facing == "up":
                hitbox_pos[1] -= self.rect.height
            elif self.facing == "down":
                hitbox_pos[1] += self.rect.height

            self.hitbox = pygame.Rect(hitbox_pos, hitbox_size)
            print(f"Player Rect: {self.rect}")
            print(f"Attack Hitbox: {self.hitbox}")

            for enemy in enemy_group:
                print(f"Checking collision with {enemy}")
                print(f"Enemy Hurtbox: {enemy.hurtbox}")
                if self.hitbox.colliderect(enemy.hurtbox):
                    print("HIT!")
                    enemy.take_damage(1, self)

    def is_adjacent_to(self, other_sprite):
        """
        Checks if the player is adjacent to another sprite and facing it.
        """
        # Create a hitbox in the direction the player is facing
        hitbox_size = (self.rect.width, self.rect.height)
        hitbox_pos = list(self.rect.topleft)

        if self.facing == "right":
            hitbox_pos[0] += self.rect.width
        elif self.facing == "left":
            hitbox_pos[0] -= self.rect.width
        elif self.facing == "up":
            hitbox_pos[1] -= self.rect.height
        elif self.facing == "down":
            hitbox_pos[1] += self.rect.height

        hitbox = pygame.Rect(hitbox_pos, hitbox_size)
        return hitbox.colliderect(other_sprite.rect)

    def update(self, dt, collision_rects):
        """
        Updates the player's state and handles collision.

        Args:
            collision_rects: A list of rects to check for collisions.
        """
        now = pygame.time.get_ticks()

        # Cooldown attack
        if self.attacking and now - self.attack_timer > self.attack_cooldown:
            self.attacking = False
            self.hitbox = None

        # Input processing
        if not self.attacking:
            dx, dy = 0, 0
            is_moving = bool(self.move_dir)

            if "right" in self.move_dir:
                dx += self.spd
                self.facing = "right"
            if "left" in self.move_dir:
                dx -= self.spd
                self.facing = "left"
            if "up" in self.move_dir:
                dy -= self.spd
                self.facing = "up"
            if "down" in self.move_dir:
                dy += self.spd
                self.facing = "down"

            # Apply friction
            self.vel *= self.friction

            # --- Horizontal Movement and Collision ---
            if not self.collidable.check_collision(dx=dx):
                self.pos.x += dx
            self.rect.x = int(self.pos.x)

            # --- Vertical Movement and Collision ---
            if not self.collidable.check_collision(dy=dy):
                self.pos.y += dy
            self.rect.y = int(self.pos.y)

            # --- Animation ---
            if is_moving:
                self.state = f"walk_{self.facing}"
            else:
                self.state = f"idle_{self.facing}"

        self.update_animation(dt)
        super().update(dt)
