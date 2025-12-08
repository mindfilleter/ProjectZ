from importlib import resources

import pytmx

# We need to import Pygame so we can use the pygame.Rect object!
import pygame


def load_map(map_name):
    """Loads a TMX map and returns a TiledMap object."""
    with resources.path("projectz.assets", map_name) as map_path:
        return pytmx.load_pygame(map_path, pixelalpha=True)


def get_collision_rects(tiled_map):
    """
    Reads the object layer called 'walkable' and returns a list of Pygame Rects.
    These Rects will be used to stop the player from walking into walls!
    """
    collision_rects = []

    # 1. Try to find the layer named "walkable" in the map data.
    try:
        walkable_layer = tiled_map.get_layer_by_name("walkable")
    except ValueError:
        # If the layer isn't found, we just return an empty list. No crash!
        print("Warning: 'walkable' object layer not found in map.")
        return collision_rects

    # 2. Loop through every object the artist drew on that layer.
    for obj in walkable_layer:
        # 3. Create a Pygame Rect object from the object's position (x, y)
        # and size (width, height).
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        collision_rects.append(rect)

    return collision_rects


def get_exit_rects(tiled_map):
    """
    Reads the object layer called 'exits' and returns a list of Tiled objects.
    These objects will be used to trigger a map change!
    """
    exits = []

    # 1. Try to find the layer named "exits" in the map data.
    try:
        exit_layer = tiled_map.get_layer_by_name("exits")
    except ValueError:
        # If the layer isn't found, we just return an empty list. No crash!
        return exits

    # 2. Loop through every object the artist drew on that layer.
    for obj in exit_layer:
        exits.append(obj)

    return exits
