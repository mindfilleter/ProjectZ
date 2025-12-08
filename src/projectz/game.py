from importlib import resources
import pytmx
import pygame
from pygame import display
from pygame import event
from pygame import time
from pygame import sprite
import pyscroll
from pyscroll.data import TiledMapData
from projectz import map

# --- Pygame Setup ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# --- Game Classes ---


class Game:

    TARGET_FPS = 60

    def __init__(self, config):
        self.config = config
        self.clock = time.Clock()
        self.running = True

        # Create the screen and a rendering surface
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # pyscroll setup
        self.map_data = None
        self.map_layer = None
        self.group = None

        self.player = Player()

        # For collisions
        self.tiled_map = None
        self.collision_rects = []
        self.exits = []

    def change_map(self, map_name, player_x, player_y):
        # pyscroll setup
        self.map_data = None
        self.map_layer = None
        self.group = None

        # For collisions
        self.tiled_map = None
        self.collision_rects = []
        self.exits = []

        # Load the map data for pyscroll
        with resources.path("projectz.assets", map_name) as map_path:
            tmx_map = pytmx.util_pygame.load_pygame(map_path)
            self.map_data = TiledMapData(tmx_map)

        # Create the map layer (renderer)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.surface.get_size())

        # Find the index of the 'ground' layer from the visible tile layers.
        # This will be used to correctly layer the player sprite.
        try:
            ground_layer_index = next(
                i for i, layer in enumerate(tmx_map.visible_layers)
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name == 'ground'
            )
        except StopIteration:
            print("Warning: 'ground' layer not found. Defaulting player layer to 0.")
            ground_layer_index = 0
        
        self.player.pos.x = player_x * 16
        self.player.pos.y = player_y * 16

        # Create the pyscroll group and add the player
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=ground_layer_index)
        self.group.add(self.player)

        # Load the map for collisions
        self.tiled_map = map.load_map(map_name)
        self.collision_rects = map.get_collision_rects(self.tiled_map)
        self.exits = map.get_exit_rects(self.tiled_map)

    def check_exits(self):
        for exit in self.exits:
            exit_rect = pygame.Rect(exit.x, exit.y, exit.width, exit.height)
            if self.player.rect.colliderect(exit_rect):
                self.change_map(exit.properties["to_map"], exit.properties["to_x"], exit.properties["to_y"])
                break

    def start(self):
        self.change_map("map.tmx", 10, 10)

        # This while loop is like the Scratch 'forever' block!
        while self.running:
            self.clock.tick(Game.TARGET_FPS)

            for pygame_event in event.get():
                if pygame_event.type == pygame.QUIT:
                    self.running = False
                self.player.handle_event(pygame_event)

            self.player.update(self.collision_rects)
            self.check_exits()

            # Center the map on the player
            self.group.center(self.player.rect.center)

            # Drawing Step:
            self.surface.fill((0, 0, 0))
            self.group.draw(self.surface)

            # Scale the rendering surface to the screen
            pygame.transform.scale(self.surface, self.screen.get_size(), self.screen)
            pygame.display.flip()


class Player(sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.pos = pygame.math.Vector2(16, 16)
        self.vel = pygame.math.Vector2(0, 0)
        self.spd = 4
        self.friction = 0.5
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y, 16, 16)
        self.move_dir = []

        # Load the spritesheet
        with resources.path("projectz.assets", "player.png") as sheet_path:
            spritesheet = pygame.image.load(sheet_path).convert_alpha()

        # Define the area of the single frame to grab
        frame_rect = pygame.Rect(32, 0, 16, 16)  # 3rd frame, 1st row

        # Create a new surface with just the frame we want
        self.image = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
        self.image.blit(spritesheet, (0, 0), frame_rect)


    def handle_event(self, pygame_event):
        if pygame_event.type == pygame.KEYDOWN:
            if pygame_event.key == pygame.K_d and "right" not in self.move_dir:
                self.move_dir.append("right")
            if pygame_event.key == pygame.K_a and "left" not in self.move_dir:
                self.move_dir.append("left")
            if pygame_event.key == pygame.K_w and "up" not in self.move_dir:
                self.move_dir.append("up")
            if pygame_event.key == pygame.K_s and "down" not in self.move_dir:
                self.move_dir.append("down")

        if pygame_event.type == pygame.KEYUP:
            if pygame_event.key == pygame.K_d and "right" in self.move_dir:
                self.move_dir.remove("right")
            if pygame_event.key == pygame.K_a and "left" in self.move_dir:
                self.move_dir.remove("left")
            if pygame_event.key == pygame.K_w and "up" in self.move_dir:
                self.move_dir.remove("up")
            if pygame_event.key == pygame.K_s and "down" in self.move_dir:
                self.move_dir.remove("down")

    # We now accept the list of collision rects!
    def update(self, collision_rects):

        # --- 1. Calculate the change in velocity (vx/vy) ---
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

        # --- 2. Move horizontally and check for collisions ---
        prev_pos = self.pos.copy()
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)

        # NEW: A quick collision check example!
        for wall in collision_rects:
            # Check if the player's rect has collided with any wall rect
            if self.rect.colliderect(wall):
                self.pos.x = prev_pos.x
                self.rect.x = int(self.pos.x)
                self.vel.x = 0  # Stop the horizontal movement

        # --- 3. Move vertically and check for collisions ---
        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)

        # NEW: Vertical collision check
        for wall in collision_rects:
            if self.rect.colliderect(wall):
                self.pos.y = prev_pos.y
                self.rect.y = int(self.pos.y)
                self.vel.y = 0  # Stop the vertical movement

    def draw(self, surface):
        # Pyscroll handles drawing the sprite's image at its rect.
        # We just need to have a self.image and self.rect.
        # The red rectangle is now created in __init__ as self.image
        pass
