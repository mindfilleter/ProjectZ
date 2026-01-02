"""
This module provides a data-driven animation system for Pygame sprites.

It uses JSON files to define sprite animations, allowing for easy modification of
animation properties without changing the game's source code. The system supports
variable frame durations, looping, and other special commands.

The JSON file format is as follows:
{
  "head": {
    "frame_width": 16,
    "frame_height": 16
  },
  "animations": {
    "walk_down": [
      [0, 100],
      [1, 100],
      ["goto", 0]
    ],
    "walk_up": [
      [2, 100],
      [3, 100],
      ["goto", 0]
    ]
  }
}
"""
import json
from importlib import resources

import pygame


class Animation:
    def __init__(self, spritesheet, animation_data):
        self.spritesheet = spritesheet
        self.animation_data = animation_data
        self.state = "idle_down"
        self.frame_width = self.animation_data["head"]["frame_width"]
        self.frame_height = self.animation_data["head"]["frame_height"]
        self.animation_timer = 0
        self.animation_frame_index = 0
        self.image = None
        self.set_sprite()

    @classmethod
    def from_json(cls, spritesheet_path, spritesheet):
        animation_data_path = f"{spritesheet_path}.spritesheet.json"
        try:
            with resources.path(
                "projectz.assets", animation_data_path
            ) as json_path:
                with open(json_path) as f:
                    animation_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading animation data: {e}")
            return None
        return cls(spritesheet, animation_data)

    def set_sprite(self):
        animation = self.animation_data["animations"][self.state]
        frame_data = animation[self.animation_frame_index]
        frame_index = frame_data[0]
        spritesheet_width = self.spritesheet.get_width()
        cols = spritesheet_width // self.frame_width
        x = (frame_index % cols) * self.frame_width
        y = (frame_index // cols) * self.frame_height
        frame_rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
        self.image = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
        self.image.blit(self.spritesheet, (0, 0), frame_rect)

    def update(self, dt):
        self.animation_timer += dt * 1000  # Convert to milliseconds
        animation = self.animation_data["animations"][self.state]
        frame_data = animation[self.animation_frame_index]

        duration = 100  # Default duration in ms
        if len(frame_data) > 1 and isinstance(frame_data[1], int):
            duration = frame_data[1]

        if self.animation_timer > duration:
            self.animation_timer = 0
            self.animation_frame_index += 1

            # Loop or process commands
            if self.animation_frame_index >= len(animation):
                self.animation_frame_index = 0  # Default loop
            
            frame_data = animation[self.animation_frame_index]
            if isinstance(frame_data[0], str):
                command = frame_data[0]
                if command == "goto":
                    self.animation_frame_index = frame_data[1]
                # Add other commands here
            
            self.set_sprite()
