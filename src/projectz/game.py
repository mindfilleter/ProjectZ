"""
This module contains the primary game logic and classes.
"""

# Python Standard Library Dependencies
import abc
from importlib import resources
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
from projectz.npc import WanderingNPC
from projectz.player import Player
from projectz.player_input import PlayerMovementConsumer, PlayerAttackConsumer
from projectz.system_input import SystemEventConsumer
from projectz.gamestates import GameStates
from projectz.logger import logger
from projectz.state_input import (
    ExploringEventConsumer,
    PausedEventConsumer,
    InventoryEventConsumer,
    DialogEventConsumer,
)


pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class GameState(abc.ABC):
    def __init__(self, game):
        self.game = game

    @abc.abstractmethod
    def update(self, dt): ...

    @abc.abstractmethod
    def draw(self): ...

    def on_enter(self):
        """
        Called when the game state is entered.
        """
        pass

    def on_exit(self):
        """
        Called when the game state is exited.
        """
        pass


class MapState(GameState):
    def __init__(self, game):
        super().__init__(game)

    def update(self, dt):
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
        self.consumer = PausedEventConsumer(self.game)

    def on_enter(self):
        self.game.register_consumer(pygame.KEYDOWN, self.consumer)
        self.game.register_consumer(pygame.KEYUP, self.consumer)

    def on_exit(self):
        self.game.unregister_consumer(pygame.KEYDOWN, self.consumer)
        self.game.unregister_consumer(pygame.KEYUP, self.consumer)

    def update(self, dt):
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
            self.rect.x = (inv_rect.x + inv_rect.x // 2) + self.id[
                0
            ] * self.space_size[0]
            self.rect.y = (inv_rect.y + inv_rect.y // 2) + self.id[
                1
            ] * self.space_size[1]

        def update(self, dt):
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
        self.consumer = InventoryEventConsumer(self.game, self)

        # --- Inventory Setup ---
        self.image = pygame.Surface((200, 250)).convert_alpha()
        self.image.fill((0, 0, 0, 200))
        self.rows = 4
        self.cols = 5
        self.inv_space_size = (
            self.image.get_width() // self.rows,
            self.image.get_height() // self.cols,
        )
        self.rect = self.image.get_rect(topleft=(20, 20))
        self.items = []

    def on_enter(self):
        self.game.register_consumer(pygame.KEYDOWN, self.consumer)

    def on_exit(self):
        self.game.unregister_consumer(pygame.KEYDOWN, self.consumer)

    def add_random_item(self):
        self.items.append(
            self.Item(
                (
                    random.randint(0, self.rows - 1),
                    random.randint(0, self.cols - 1),
                ),
                self.inv_space_size,
                self.rect,
            )
        )

    def update(self, dt):
        for item in self.items:
            if item.show == 1:
                item.update(dt)
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


class DialogState(GameState):
    def __init__(self, game, npc):
        super().__init__(game)
        self.npc = npc
        self.consumer = DialogEventConsumer(self.game, self)
        self.font = pygame.font.Font(None, 24)
        self.dialog_index = 0
        self.text = None
        self.text_rect = None
        self._render_text()

        self.dialog_box = pygame.Rect(
            (0, 0),
            (SCREEN_WIDTH // 2 - 20, self.game.TILE_SIZE * 3),
        )
        self.dialog_box.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)
        self.text_rect.center = self.dialog_box.center

        self.chevron = self.font.render(">", True, (255, 255, 255))
        self.chevron_rect = self.chevron.get_rect(
            midleft=(self.dialog_box.right - 20, self.dialog_box.centery)
        )
        self.chevron_visible = True
        self.chevron_timer = pygame.time.get_ticks()

    def _render_text(self):
        self.text = self.font.render(
            self.npc.dialogs[self.dialog_index], True, (255, 255, 255)
        )
        self.text_rect = self.text.get_rect(
            center=(
                SCREEN_WIDTH // 4,
                SCREEN_HEIGHT // 4,
            )
        )

    def advance_dialog(self):
        self.dialog_index += 1
        if self.dialog_index < len(self.npc.dialogs):
            self._render_text()
            self.text_rect.center = self.dialog_box.center
        else:
            self.game.change_state(GameStates.Exploring)

    def on_enter(self):
        self.game.register_consumer(pygame.KEYDOWN, self.consumer)

    def on_exit(self):
        self.game.unregister_consumer(pygame.KEYDOWN, self.consumer)

    def update(self, dt):
        self.chevron_visible = not self.chevron_visible
        self.chevron_timer = pygame.time.get_ticks()

    def draw(self):
        self.game.game_states[GameStates.Exploring].draw()
        pygame.draw.rect(
            self.game.surface, (0, 0, 0), self.dialog_box, border_radius=5
        )
        self.game.surface.blit(self.text, self.text_rect)
        if self.chevron_visible:
            self.game.surface.blit(self.chevron, self.chevron_rect)


class ExploringState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.player_movement_consumer = PlayerMovementConsumer(
            self.game, self.game.player
        )
        self.player_attack_consumer = PlayerAttackConsumer(
            self.game, self.game.player, self.game.enemy_group
        )
        self.exploring_consumer = ExploringEventConsumer(self.game)

    def on_enter(self):
        self.game.register_consumer(
            pygame.KEYDOWN, self.player_movement_consumer
        )
        self.game.register_consumer(
            pygame.KEYUP, self.player_movement_consumer
        )
        self.game.register_consumer(
            pygame.KEYDOWN, self.player_attack_consumer
        )
        self.game.register_consumer(pygame.KEYDOWN, self.exploring_consumer)

    def on_exit(self):
        self.game.player.move_dir.clear()
        self.game.unregister_consumer(
            pygame.KEYDOWN, self.player_movement_consumer
        )
        self.game.unregister_consumer(
            pygame.KEYUP, self.player_movement_consumer
        )
        self.game.unregister_consumer(
            pygame.KEYDOWN, self.player_attack_consumer
        )
        self.game.unregister_consumer(pygame.KEYDOWN, self.exploring_consumer)

    def check_for_dialog(self):
        for npc in self.game.npc_group:
            if self.game.player.is_adjacent_to(npc):
                self.game.game_states[GameStates.Dialog] = DialogState(
                    self.game, npc
                )
                self.game.change_state(GameStates.Dialog)
                break

    def update(self, dt):
        self.game.player.update(dt, self.game.map.collision_rects)
        self.game.hud.update()
        self.game.enemy_group.update(dt, self.game.map.collision_rects)
        self.game.npc_group.update(dt, self.game.map.collision_rects)
        self.game.check_exits()
        if self.game.group:
            self.game.group.center(self.game.player.rect.center)

    def draw(self):
        self.game.surface.fill((0, 0, 0))
        if self.game.group:
            self.game.group.draw(self.game.surface)
            logger.debug(f"Camera View: {self.game.group.view.topleft}")
        if self.game.player.hitbox:
            # Get the camera's view rect
            camera_view = self.game.group.view
            # Translate the hitbox rect by the camera's view
            display_hitbox = self.game.player.hitbox.move(
                -camera_view.x, -camera_view.y
            )
            pygame.draw.rect(
                self.game.surface, (255, 0, 0, 150), display_hitbox
            )

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
        self.state = None
        self.event_consumers = {}

        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.npc_group = pygame.sprite.Group()

        self.player = Player(self, self.TILE_SIZE)
        self.player_group.add(self.player)  # Player is added to its own group
        self.hud = HUD(self.player)

        self.game_states = {
            GameStates.Map: MapState(self),
            GameStates.Paused: PausedState(self),
            GameStates.Exploring: ExploringState(self),
            GameStates.Inventory: InventoryState(self),
            GameStates.Dialog: None,  # Initialized when needed
        }

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.map_data = None
        self.map_layer = None
        self.group = None  # This is the PyscrollGroup for map and player

        # --- Sprite Groups ---

        self.map = None

        self.register_consumer(pygame.QUIT, SystemEventConsumer(self))

    def register_consumer(self, event_type, consumer):
        if event_type not in self.event_consumers:
            self.event_consumers[event_type] = []
        self.event_consumers[event_type].append(consumer)

    def unregister_consumer(self, event_type, consumer):
        if event_type in self.event_consumers:
            if consumer in self.event_consumers[event_type]:
                self.event_consumers[event_type].remove(consumer)

    def change_state(self, new_state):
        print(new_state)
        if self.state and self.game_states.get(self.state):
            self.game_states[self.state].on_exit()
        self.state = new_state
        event.clear()
        if self.game_states.get(self.state):
            self.game_states[self.state].on_enter()

    def _reset_map_state(self):
        """
        Resets the map-related attributes and clears sprites when changing maps.
        """
        self.map_data = None
        self.map_layer = None
        self.group = None
        self.map = None

        # Clear all enemies when changing maps!
        self.enemy_group.empty()
        self.npc_group.empty()

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

        self.map = map.Map(map_name)

        try:
            with resources.path("projectz.assets", map_name) as map_path:
                tmx_map = self.map.tiled_map
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
                if isinstance(layer, pytmx.TiledTileLayer)
                and layer.name == "ground"
            )
        except StopIteration:
            print(
                "Warning: 'ground' layer not found. Defaulting player layer to 0."
            )
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
        pass

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
        self.npc_spawn_logic()

    def check_exits(self):
        """
        Checks if the player is colliding with any exits.
        """
        for exit_obj in self.map.exits:
            exit_rect = pygame.Rect(
                exit_obj.x, exit_obj.y, exit_obj.width, exit_obj.height
            )
            if self.player.rect.colliderect(exit_rect):
                # Ensure properties exist before accessing
                if (
                    "to_map" in exit_obj.properties
                    and "to_x" in exit_obj.properties
                    and "to_y" in exit_obj.properties
                ):
                    self.change_map(
                        exit_obj.properties["to_map"],
                        int(exit_obj.properties["to_x"]),
                        int(exit_obj.properties["to_y"]),
                    )
                    break
                else:
                    print(
                        f"Warning: Exit object {exit_obj.name} is missing 'to_map', 'to_x', or 'to_y' properties."
                    )

    def enemy_spawn_logic(self):
        """
        Spawns enemies based on the spawn points defined in the map.
        """
        for spawn in self.map.enemy_spawns:
            slime_type = spawn.properties.get("slime_type", "red")
            new_object = Enemy(self, spawn.x, spawn.y, slime_type, self.player)
            self.enemy_group.add(new_object)
            self.group.add(new_object)

    def npc_spawn_logic(self):
        """
        Spawns NPCs based on the spawn points defined in the map.
        """
        for spawn in self.map.npc_spawns:
            wandering_area_name = spawn.properties.get("wandering_area")
            if wandering_area_name in self.map.npc_wandering_areas:
                boundaries = self.map.npc_wandering_areas[wandering_area_name]
                new_npc = WanderingNPC(self, spawn, boundaries)
                self.npc_group.add(new_npc)
                self.group.add(new_npc)

    def start(self):
        """
        Starts the game loop.
        """
        self.change_map("map.tmx")
        self.change_state(GameStates.Exploring)

        while self.running:
            dt = self.clock.tick(Game.TARGET_FPS) / 1000.0

            for pygame_event in event.get():
                if pygame_event.type in self.event_consumers:
                    for consumer in self.event_consumers[pygame_event.type]:
                        consumer.handle_event(pygame_event)

            current_state = self.game_states.get(self.state)
            if current_state:
                current_state.update(dt)
                current_state.draw()

            pygame.transform.scale(
                self.surface, self.screen.get_size(), self.screen
            )
            pygame.display.flip()
