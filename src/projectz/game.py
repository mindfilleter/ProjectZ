"""
This module contains the primary game logic and classes.
"""

from importlib import resources
import pytmx
import pygame
import math
import random
from pygame import event
from pygame import time
from pygame import sprite
import pyscroll
from pyscroll.data import TiledMapData
from projectz import map


pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# --- GLOBAL SPRITE GROUPS ---
# We keep these outside the class so they are easy to access
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
# ----------------------------


class Game:
    """
    Represents the main game loop and state.
    """

    TARGET_FPS = 60
    TILE_SIZE = 16

    def __init__(self, config):
        """
        Initializes the game.
        """
        self.config = config
        self.clock = time.Clock()
        self.running = True

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.map_data = None
        self.map_layer = None
        self.group = None  # This is the PyscrollGroup for map and player

        self.player = Player(self.TILE_SIZE)
        player_group.add(self.player)  # Player is added to its own group

        self.tiled_map = None
        self.collision_rects = []
        self.exits = []

        self.enemys_to_spawn = 2

    def _reset_map_state(self):
        """
        Resets the map-related attributes and clears sprites when changing maps.
        """
        self.map_data = None
        self.map_layer = None
        self.group = None
        self.tiled_map = None
        self.collision_rects = []
        self.exits = []

        # Clear all enemies when changing maps!
        enemy_group.empty()

    def _load_map_visuals(self, map_name):
        """
        Loads the visual components of the map.

        Args:
            map_name: The name of the map to load.

        Returns:
            A tuple containing the tmx_map and map_layer.
        """
        # Ensure 'map_name' is a string before using it in f-string
        if not isinstance(map_name, str):
            map_name = "default_map.tmx"  # Use a safe default

        try:
            with resources.path("projectz.assets", map_name) as map_path:
                tmx_map = pytmx.util_pygame.load_pygame(map_path)
                self.map_data = TiledMapData(tmx_map)
        except FileNotFoundError:
            print(
                f"Error: Map file '{map_name}' not found in assets. Check project_structure."
            )
            # Create an empty TiledMapData or handle error gracefully
            return None, None
        except Exception as e:
            print(f"Error loading TMX map '{map_name}': {e}")
            return None, None

        self.map_layer = pyscroll.BufferedRenderer(
            self.map_data, self.surface.get_size()
        )
        return tmx_map, self.map_layer

    def _setup_player_and_group(self, tmx_map, map_layer, player_x, player_y):
        """
        Sets up the player and the sprite group.

        Args:
            tmx_map: The loaded tmx map.
            map_layer: The rendered map layer.
            player_x: The player's starting x position.
            player_y: The player's starting y position.
        """
        if tmx_map is None or map_layer is None:
            # Handle case where map loading failed
            return

        try:
            ground_layer_index = next(
                i
                for i, layer in enumerate(tmx_map.visible_layers)
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "ground"
            )
        except StopIteration:
            print("Warning: 'ground' layer not found. Defaulting player layer to 0.")
            ground_layer_index = 0

        if player_x is not None and player_y is not None:
            self.player.pos.x = player_x * self.TILE_SIZE
            self.player.pos.y = player_y * self.TILE_SIZE
        else:
            player_start = tmx_map.get_object_by_name("player_start")
            if player_start:
                self.player.pos.x = player_start.x
                self.player.pos.y = player_start.y
            else:
                # Default fallback if no start position is found
                self.player.pos.x = 10 * self.TILE_SIZE
                self.player.pos.y = 10 * self.TILE_SIZE

        self.group = pyscroll.PyscrollGroup(
            map_layer=map_layer, default_layer=ground_layer_index
        )
        self.group.add(self.player)  # Player is added to the pyscroll group

    def _load_map_objects(self, map_name):
        """
        Loads the map's collision and exit objects.

        Args:
            map_name: The name of the map to load.
        """
        self.tiled_map = map.load_map(map_name)
        if self.tiled_map is not None:
            self.collision_rects = map.get_collision_rects(self.tiled_map)
            self.exits = map.get_exit_rects(self.tiled_map)
        else:
            self.collision_rects = []
            self.exits = []

    def change_map(self, map_name, player_x=None, player_y=None):
        """
        Changes the current map.

        Args:
            map_name: The name of the map to load.
            player_x: The player's starting x position.
            player_y: The player's starting y position.
        """
        self._reset_map_state()
        tmx_map, map_layer = self._load_map_visuals(map_name)

        if tmx_map is None or map_layer is None:
            # If map loading failed, stop here.
            return

        self._setup_player_and_group(tmx_map, map_layer, player_x, player_y)
        self._load_map_objects(map_name)

        # Call the spawn logic right after changing the map!
        self.enemy_spawn_logic()

    def check_exits(self):
        """
        Checks if the player is colliding with any exits.
        """
        for exit in self.exits:
            exit_rect = pygame.Rect(exit.x, exit.y, exit.width, exit.height)
            if self.player.rect.colliderect(exit_rect):
                # Ensure properties exist before accessing
                if (
                    "to_map" in exit.properties
                    and "to_x" in exit.properties
                    and "to_y" in exit.properties
                ):
                    self.change_map(
                        exit.properties["to_map"],
                        int(exit.properties["to_x"]),
                        int(exit.properties["to_y"]),
                    )
                    break
                else:
                    print(
                        f"Warning: Exit object {exit.name} is missing 'to_map', 'to_x', or 'to_y' properties."
                    )

    def enemy_spawn_logic(self):  # Removed parameters and used self attributes
        """
        Spawns enemies randomly and adds them to the enemy_group.
        """
        for i in range(self.enemys_to_spawn):
            # Spawn enemies near the player's current location,
            # but away from the center of the screen
            spawn_x = self.player.rect.x + random.randint(-200, 200)
            spawn_y = self.player.rect.y + random.randint(-200, 200)

            # Ensure enemies are spawned within the current map boundaries
            if self.tiled_map:
                map_width = self.tiled_map.width * self.tiled_map.tilewidth
                map_height = self.tiled_map.height * self.tiled_map.tileheight
                spawn_x = max(0, min(spawn_x, map_width - 16))  # 16 is enemy width
                spawn_y = max(0, min(spawn_y, map_height - 16))  # 16 is enemy height

            new_object = Enemy(spawn_x, spawn_y, "red slime", self.player)

            # This is how the enemies are added to the group for drawing/updating!
            enemy_group.add(new_object)

    def start(self):
        """
        Starts the game loop.
        """
        self.change_map("map.tmx")

        while self.running:
            self.clock.tick(Game.TARGET_FPS)

            for pygame_event in event.get():
                if pygame_event.type == pygame.QUIT:
                    self.running = False
                self.player.handle_event(pygame_event)

            # --- UPDATE STEP (Movement) ---
            self.player.update(self.collision_rects)

            # FIX 1: You must call .update() on the enemy_group to make enemies move!
            # The *args passed here will go to the Enemy.update method.
            enemy_group.update(self.collision_rects)

            self.check_exits()

            # Ensure the group exists before centering
            if self.group:
                self.group.center(self.player.rect.center)

            # --- DRAW STEP (Rendering) ---
            self.surface.fill((0, 0, 0))

            # This draws the map tiles and the player (if group exists)
            if self.group:
                self.group.draw(self.surface)

            # This draws all the enemies that you added to the global enemy_group!
            enemy_group.draw(self.surface)

            pygame.transform.scale(self.surface, self.screen.get_size(), self.screen)
            pygame.display.flip()


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


class Enemy(sprite.Sprite):
    def __init__(self, x, y, type, player):
        # 1. Initialize the base Sprite class
        super().__init__()

        # 2. Set the 'Costume' (the image) for the sprite.
        self.image = pygame.Surface((16, 16)).convert_alpha()
        self.image.fill((200, 50, 50))  # A dark red enemy!

        # Use floating point numbers for smooth movement
        self.x = float(x)
        self.y = float(y)
        self.type = type
        self.dir = 0
        self.spd = 0.5
        self.friction = 0.5

        # 3. The 'rect' is used for positioning and collision checking.
        self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))

        self.player = player  # Store the player so we can chase them

    def update(self, collision_rects):

        # Calculate the distance and direction to the player
        # We target the player's center for smooth tracking
        self.dx = (
            self.player.rect.centerx - self.x
        )  # Calculate difference (Player - Enemy)
        self.dy = (
            self.player.rect.centery - self.y
        )  # Calculate difference (Player - Enemy)

        # Calculate the angle (in radians) to the player
        self.dir = math.atan2(self.dy, self.dx)

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
