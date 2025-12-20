"""
This module contains the primary game logic and classes.
"""

# Python Standard Library Dependencies
import abc
from importlib import resources
import enum
import math
import random

# 3rd Party Dependencies
from pygame import event
from pygame import sprite
from pygame import time
from pyscroll.data import TiledMapData
import pygame
import pyscroll
import pytmx

# Module Dependencies
from projectz import map
from projectz.enemies import Enemy
from projectz.hud import HUD
from projectz.player import Player


pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class GameStates(enum.Enum):
    Map = "Map"
    Paused = "Paused"
    Exploring = "Exploring"
    Inventory = "Inventory"


class GameState(abc.ABC):
    def __init__(self, game):
        self.game = game

    @abc.abstractmethod
    def handle_input(self, pygame_event): ...

    @abc.abstractmethod
    def update(self): ...

    @abc.abstractmethod
    def draw(self): ...


class MapState(GameState):
    def __init__(self, game):
        super().__init__(game)

    def handle_input(self, pygame_event):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class PausedState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render("Paused", True, (255, 255, 255))
        self.text_rect = self.text.get_rect(
            center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)
        )

    def handle_input(self, pygame_event):
        if pygame_event.type == pygame.KEYDOWN:
            if pygame_event.key == pygame.K_p:
                self.game.state = GameStates.Exploring

    def update(self):
        pass

    def draw(self):
        self.game.game_states[GameStates.Exploring].draw()
        self.game.surface.blit(self.text, self.text_rect)


class InventoryState(GameState):

    class Item(sprite.Sprite):
        def __init__(self, id, space_size, inv_rect, *groups):
            super().__init__(*groups)
            self.image = pygame.Surface((20, 20)).convert_alpha()
            self.rect = self.image.get_rect()
            self.show = 0
            self.color = (0, 0, 255, self.show * 255)
            self.image.fill(self.color)
            self.id = id
            self.space_size = space_size
            self.rect.x = (inv_rect.x + inv_rect.x // 2) + self.id[0] * self.space_size[
                0
            ]
            self.rect.y = (inv_rect.y + inv_rect.y // 2) + self.id[1] * self.space_size[
                1
            ]

        def update(self):
            mousex, mousey = pygame.mouse.get_pos()
            if self.show == 1:
                self.color = (0, 0, 255, self.show * 255)
                self.image.fill(self.color)
                if self.rect.collidepoint(mousex, mousey):
                    self.hovering = 1
                else:
                    self.hovering = 0

            else:
                self.color = (0, 0, 255, self.show * 255)
                self.image.fill(self.color)

    def __init__(self, game):
        super().__init__(game)

        # --- Inventory Setup ---
        self.image = pygame.Surface((200, 250)).convert_alpha()
        self.image.fill((0, 0, 0, 200))
        self.rows = 4
        self.cols = 5
        self.inv_space_size = (
            self.image.get_width() // self.rows,
            self.image.get_height() // self.cols,
        )

        # FIX 1: I finished the coordinate numbers here.
        # In your code it said "topleft=", which confuses Python.
        self.rect = self.image.get_rect(topleft=(20, 20))

        # We can use Item here because we are still inside the __init__ function!

        self.items = []

    def handle_input(self, pygame_event):
        if pygame_event.type == pygame.KEYDOWN:
            if pygame_event.key == pygame.K_e:
                self.game.state = GameStates.Exploring
            if pygame_event.key == pygame.K_a:
                self.new_object = self.Item(
                    (
                        random.randint(0, self.rows - 1),
                        random.randint(0, self.cols - 1),
                    ),
                    self.inv_space_size,
                    self.rect,
                )
                self.items.append(self.new_object)

    def update(self):
        for item in self.items:
            if item.show == 1:
                item.update()
        for item in self.items:
            if item in self.items:
                item.show = 1
            else:
                item.show = 0

    def draw(self):
        self.game.game_states[GameStates.Exploring].draw()

        self.game.surface.blit(self.image, self.rect)

        for item in self.items:
            self.game.surface.blit(item.image, item.rect)


class ExploringState(GameState):
    def __init__(self, game):
        super().__init__(game)

    def handle_input(self, pygame_event):
        self.game.player.handle_event(pygame_event)
        if pygame_event.type == pygame.KEYDOWN:
            if pygame_event.key == pygame.K_p:
                self.game.state = GameStates.Paused
            if pygame_event.key == pygame.K_e:
                self.game.state = GameStates.Inventory

    def update(self):
        self.game.player.update(self.game.collision_rects)
        self.game.hud.update()
        self.game.enemy_group.update(self.game.collision_rects)
        self.game.check_exits()
        if self.game.group:
            self.game.group.center(self.game.player.rect.center)

    def draw(self):
        self.game.surface.fill((0, 0, 0))
        if self.game.group:
            self.game.group.draw(self.game.surface)
        self.game.hud.draw(self.game.surface)


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
        self.state = GameStates.Exploring
        self.game_states = {
            GameStates.Map: MapState(self),
            GameStates.Paused: PausedState(self),
            GameStates.Exploring: ExploringState(self),
            GameStates.Inventory: InventoryState(self),
        }

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.map_data = None
        self.map_layer = None
        self.group = None  # This is the PyscrollGroup for map and player

        # --- Sprite Groups ---
        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        self.player = Player(self.TILE_SIZE)
        self.player_group.add(self.player)  # Player is added to its own group
        self.hud = HUD(self.player)

        self.tiled_map = None
        self.collision_rects = []
        self.exits = []
        self.enemy_spawns = []

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
        self.enemy_spawns = []

        # Clear all enemies when changing maps!
        self.enemy_group.empty()

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
            self.enemy_spawns = map.get_enemy_spawn_points(self.tiled_map)
        else:
            self.collision_rects = []
            self.exits = []
            self.enemy_spawns = []

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

    def enemy_spawn_logic(self):
        """
        Spawns enemies based on the spawn points defined in the map.
        """
        for spawn in self.enemy_spawns:
            slime_type = spawn.properties.get("slime_type", "red")
            new_object = Enemy(spawn.x, spawn.y, slime_type, self.player)
            self.enemy_group.add(new_object)
            self.group.add(new_object)

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

                self.game_states[self.state].handle_input(pygame_event)

            self.game_states[self.state].update()
            self.game_states[self.state].draw()

            pygame.transform.scale(self.surface, self.screen.get_size(), self.screen)
            pygame.display.flip()
