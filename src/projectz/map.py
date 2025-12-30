"""
This module contains functions for loading and interacting with TMX maps.
"""

from importlib import resources

import pytmx

import pygame


class Map:
    def __init__(self, map_name):
        self.tiled_map = load_map(map_name)
        self.collision_rects = get_collision_rects(self.tiled_map)
        self.exits = get_exit_rects(self.tiled_map)
        self.enemy_spawns = get_enemy_spawn_points(self.tiled_map)
        self.npc_spawns = get_npc_spawn_points(self.tiled_map)
        self.npc_wandering_areas = get_npc_wandering_areas(self.tiled_map)

    def is_wall(self, x, y):
        """
        Checks if a point is inside a wall collision rect.

        Args:
            x: The x coordinate in pixels.
            y: The y coordinate in pixels.

        Returns:
            True if the point is a wall, False otherwise.
        """
        for rect in self.collision_rects:
            if rect.collidepoint(x, y):
                return True
        return False


def load_map(map_name):
    """
    Loads a TMX map.

    Args:
        map_name: The name of the map to load.

    Returns:
        A TiledMap object.
    """
    with resources.path("projectz.assets", map_name) as map_path:
        return pytmx.load_pygame(map_path, pixelalpha=True)


def get_collision_rects(tiled_map):
    """
    Gets the collision rects from a Tiled map.

    Args:
        tiled_map: The TiledMap object to get the collision rects from.

    Returns:
        A list of pygame.Rect objects.
    """
    collision_rects = []

    try:
        walkable_layer = tiled_map.get_layer_by_name("walkable")
    except ValueError:
        print("Warning: 'walkable' object layer not found in map.")
        return collision_rects

    for obj in walkable_layer:
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        collision_rects.append(rect)

    return collision_rects


def get_exit_rects(tiled_map):
    """
    Gets the exit rects from a Tiled map.

    Args:
        tiled_map: The TiledMap object to get the exit rects from.

    Returns:
        A list of Tiled objects.
    """
    exits = []

    try:
        exit_layer = tiled_map.get_layer_by_name("exits")
    except ValueError:
        return exits

    for obj in exit_layer:
        exits.append(obj)

    return exits


def get_enemy_spawn_points(tiled_map):
    """
    Gets the enemy spawn points from a Tiled map.

    Args:
        tiled_map: The TiledMap object to get the enemy spawn points from.

    Returns:
        A list of Tiled objects.
    """
    spawns = []

    try:
        enemy_layer = tiled_map.get_layer_by_name("enemies")
    except ValueError:
        return spawns

    for obj in enemy_layer:
        spawns.append(obj)

    return spawns


def get_npc_spawn_points(tiled_map):
    """
    Gets the npc spawn points from a Tiled map.
    """
    spawns = []
    try:
        npc_layer = tiled_map.get_layer_by_name("npcs")
    except ValueError:
        return spawns
    for obj in npc_layer:
        if obj.name == "npc_spawn":
            spawns.append(obj)
    return spawns


def get_npc_wandering_areas(tiled_map):
    """
    Gets the npc wandering areas from a Tiled map.
    """
    areas = {}
    try:
        npc_layer = tiled_map.get_layer_by_name("npcs")
    except ValueError:
        return areas
    for obj in npc_layer:
        if obj.name == "wandering_area" and "area_name" in obj.properties:
            areas[obj.properties["area_name"]] = pygame.Rect(
                obj.x, obj.y, obj.width, obj.height
            )
    return areas