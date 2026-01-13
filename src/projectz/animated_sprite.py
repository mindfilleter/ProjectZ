from importlib import resources
import pygame

from projectz.animation import Animation


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, spritesheet_path, max_hp=100, *groups):
        super().__init__(*groups)
        self.spritesheet = self._load_spritesheet(spritesheet_path)
        self.animation = Animation.from_json(spritesheet_path, self.spritesheet)
        self.image = self.animation.image
        self.state = "idle_down"

        self.max_hp = max_hp
        self.current_hp = max_hp

    def take_damage(self, amount):
        """Reduces current HP by the given amount."""
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0

    def heal(self, amount):
        """Increases current HP by the given amount, up to max_hp."""
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def is_dead(self):
        """Returns True if current HP is 0 or less."""
        return self.current_hp <= 0


    def _load_spritesheet(self, path):
        try:
            with resources.path("projectz.assets", path) as sheet_path:
                spritesheet = pygame.image.load(sheet_path).convert_alpha()
                return spritesheet
        except FileNotFoundError:
            print(f"Error: {path} not found. Using red square placeholder.")
            spritesheet = pygame.Surface((32, 32), pygame.SRCALPHA)
            spritesheet.fill((255, 0, 0))
            return spritesheet

    def update_animation(self, dt):
        if self.state != self.animation.state:
            self.animation.state = self.state
            self.animation.animation_frame_index = 0

        self.animation.update(dt)
        self.image = self.animation.image
