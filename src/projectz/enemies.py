import math
import random
import pygame
from importlib import resources
from pygame import sprite

from projectz.animated_sprite import AnimatedSprite
from projectz.common import Collidable, Pathfinder


class Enemy(AnimatedSprite):
    WANDER_RADIUS = 50
    CHASE_RADIUS = 150
    ATTACK_RANGE = 40
    ATTACK_ANTICIPATION_TIME = 500  # ms
    LUNGE_DURATION = 200  # ms
    LUNGE_SPEED = 2.5
    RETREAT_DURATION = 300 # ms
    RETREAT_SPEED = 1.5


    def __init__(self, game, x, y, type, player):
        # 1. Initialize the base Sprite class
        super().__init__("slimes.png", max_hp=2)

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

        self.behavior_state = "wandering"
        self.attack_state = "approaching" 
        self.state = "idle_down" # Animation state
        self.wander_target = None
        self.attack_timer = 0
        self.lunge_direction = None


    def __repr__(self):
        return f"<Enemy type={self.type} pos={self.pos}>"

    def update(self, dt, collision_rects):
        if self.is_dead():
            self.kill()
            return
            
        if self.rect.colliderect(self.player.rect):
            self.player.take_damage(1, self)

        player_dist = self.pos.distance_to(self.player.pos)

        # Don't do anything if being knocked back
        if pygame.time.get_ticks() - self.knockback_timer < self.knockback_duration:
             self.hurtbox.topleft = self.rect.topleft
             super().update(dt)
             return

        if self.behavior_state == "wandering":
            if player_dist < self.CHASE_RADIUS:
                self.behavior_state = "chasing"
                self.attack_state = "approaching"
            else:
                self.wander()
        elif self.behavior_state == "chasing":
            if player_dist > self.CHASE_RADIUS * 1.2:  # A little buffer to prevent rapid state changes
                self.behavior_state = "wandering"
                self.path = []
            else:
                self.chase_attack_pattern()
        
        self.hurtbox.topleft = self.rect.topleft
        super().update(dt)

    def wander(self):
        is_moving = False
        if self.wander_target:
            direction = self.wander_target - self.pos
            if direction.length() < 2:
                self.wander_target = None
            else:
                is_moving = True
                if direction.length() > 0:
                    direction.normalize_ip()

                self.set_animation_direction(direction)
                movement = direction * self.spd
                if not self.collidable.check_collision(dx=movement.x, dy=movement.y):
                    self.pos += movement
                    self.rect.topleft = self.pos

        if not self.wander_target and random.randint(0, 100) < 2: # 2% chance to pick a new target
            self.wander_target = self.pos + pygame.math.Vector2(
                random.randint(-self.WANDER_RADIUS, self.WANDER_RADIUS),
                random.randint(-self.WANDER_RADIUS, self.WANDER_RADIUS),
            )
        
        if not is_moving:
            self.state = "idle_down"

    def set_animation_direction(self, direction):
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

    def chase_attack_pattern(self):
        now = pygame.time.get_ticks()
        player_dist = self.pos.distance_to(self.player.pos)

        if self.attack_state == "approaching":
            if player_dist < self.ATTACK_RANGE:
                self.attack_state = "anticipating"
                self.attack_timer = now
                self.path = []
            else:
                self.approach()
        
        elif self.attack_state == "anticipating":
            self.state = "tremble" # Stop moving
            if now - self.attack_timer > self.ATTACK_ANTICIPATION_TIME:
                self.attack_state = "lunging"
                self.attack_timer = now
                self.lunge_direction = (self.player.pos - self.pos).normalize()

        elif self.attack_state == "lunging":
            self.set_animation_direction(self.lunge_direction)
            movement = self.lunge_direction * self.LUNGE_SPEED
            if not self.collidable.check_collision(dx=movement.x, dy=movement.y):
                self.pos += movement
                self.rect.topleft = self.pos

            if now - self.attack_timer > self.LUNGE_DURATION:
                self.attack_state = "retreating"
                self.attack_timer = now

        elif self.attack_state == "retreating":
            retreat_direction = -self.lunge_direction
            self.set_animation_direction(retreat_direction)
            movement = retreat_direction * self.RETREAT_SPEED
            if not self.collidable.check_collision(dx=movement.x, dy=movement.y):
                self.pos += movement
                self.rect.topleft = self.pos
            
            if now - self.attack_timer > self.RETREAT_DURATION:
                self.attack_state = "approaching"


    def approach(self):
        # Get a new path to the player periodically
        if not self.path or random.randint(0, 100) < 2:  # 2% chance to recalculate path
            self.path = self.pathfinder.get_path(
                self.rect.topleft, self.player.rect.topleft
            )

        is_moving = False
        if self.path:
            next_point = pygame.math.Vector2(self.path[0])
            direction = next_point - self.pos

            if direction.length() < 2:
                self.path.pop(0)
                if not self.path:
                    self.state = "idle_down"
                    return
                else:
                    next_point = pygame.math.Vector2(self.path[0])
                    direction = next_point - self.pos
            
            is_moving = True
            if direction.length() > 0:
                direction.normalize_ip()

            self.set_animation_direction(direction)
            movement = direction * self.spd

            if not self.collidable.check_collision(dx=movement.x, dy=movement.y):
                self.pos += movement
                self.rect.topleft = self.pos
        if not is_moving:
            self.state = "idle_down"

