"""
This module contains the primary game logic and classes.
"""

from importlib import resources
import pytmx
import pygame
from pygame import event
from pygame import time
from pygame import sprite
import pyscroll
from pyscroll.data import TiledMapData
from projectz import map


pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


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
        self.group = None

        self.player = Player(self.TILE_SIZE)

        self.tiled_map = None
        self.collision_rects = []
        self.exits = []

    def _reset_map_state(self):
        """
        Resets the map-related attributes.
        """
        self.map_data = None
        self.map_layer = None
        self.group = None
        self.tiled_map = None
        self.collision_rects = []
        self.exits = []

    def _load_map_visuals(self, map_name):
        """
        Loads the visual components of the map.

        Args:
            map_name: The name of the map to load.

        Returns:
            A tuple containing the tmx_map and map_layer.
        """
        with resources.path("projectz.assets", map_name) as map_path:
            tmx_map = pytmx.util_pygame.load_pygame(map_path)
            self.map_data = TiledMapData(tmx_map)

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
        self.group.add(self.player)

    def _load_map_objects(self, map_name):
        """
        Loads the map's collision and exit objects.

        Args:
            map_name: The name of the map to load.
        """
        self.tiled_map = map.load_map(map_name)
        self.collision_rects = map.get_collision_rects(self.tiled_map)
        self.exits = map.get_exit_rects(self.tiled_map)

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
        self._setup_player_and_group(tmx_map, map_layer, player_x, player_y)
        self._load_map_objects(map_name)

    def check_exits(self):
        """
        Checks if the player is colliding with any exits.
        """
        for exit in self.exits:
            exit_rect = pygame.Rect(exit.x, exit.y, exit.width, exit.height)
            if self.player.rect.colliderect(exit_rect):
                self.change_map(
                    exit.properties["to_map"],
                    int(exit.properties["to_x"]),
                    int(exit.properties["to_y"]),
                )
                break

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

            self.player.update(self.collision_rects)
            self.check_exits()

            self.group.center(self.player.rect.center)

            self.surface.fill((0, 0, 0))
            self.group.draw(self.surface)

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
        self.pos = pygame.math.Vector2(tile_size, tile_size)
        self.vel = pygame.math.Vector2(0, 0)
        self.spd = 4
        self.friction = 0.5
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y, tile_size, tile_size)
        self.move_dir = []

        with resources.path("projectz.assets", "player.png") as sheet_path:
            spritesheet = pygame.image.load(sheet_path).convert_alpha()

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
        Updates the player's state.

        Args:
            collision_rects: A list of rects to check for collisions.
        """
        if "right" in self.move_dir:
            self.vel.x += self.spd
        if "left" in self.move_dir:
            self.vel.x -= self.spd
        if "up" in self.move_dir:
            self.vel.y -= self.spd
        if "down" in self.move_dir:
            self.vel.y += self.spd

        self.vel *= self.friction

        prev_pos = self.pos.copy()
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)

        for wall in collision_rects:
            if self.rect.colliderect(wall):
                self.pos.x = prev_pos.x
                self.rect.x = int(self.pos.x)
                self.vel.x = 0

        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)

        for wall in collision_rects:
            if self.rect.colliderect(wall):
                self.pos.y = prev_pos.y
                self.rect.y = int(self.pos.y)
                self.vel.y = 0

    def draw(self, surface):
        """
        Draws the player to the screen.

        Args:
            surface: The surface to draw the player on.
        """
        pass
