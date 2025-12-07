from importlib import resources

import pytmx


def load_map(map_name):
    """Loads a TMX map and returns a TiledMap object."""
    with resources.path("projectz.assets", map_name) as map_path:
        return pytmx.load_pygame(map_path, pixelalpha=True)


def render_map(surface, tiled_map):
    """Renders the TMX map on the given surface."""
    for layer in tiled_map.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tiled_map.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(
                        tile,
                        (x * tiled_map.tilewidth, y * tiled_map.tileheight),
                    )
