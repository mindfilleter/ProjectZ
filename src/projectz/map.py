"""
This module contains functions for loading and interacting with TMX maps.
"""

from importlib import resources

import pytmx

import pygame


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
