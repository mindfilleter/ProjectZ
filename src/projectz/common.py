import pygame
from pytmx.util_pygame import load_pygame
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class Collidable:
    def __init__(self, game, x, y, sprite):
        self.game = game
        self.sprite = sprite
        self.rect = self.sprite.rect

    def check_collision(self, dx=0, dy=0):
        # We need to check all four corners of the sprite
        corners = [
            (self.rect.left + dx, self.rect.top + dy),
            (self.rect.right + dx, self.rect.top + dy),
            (self.rect.left + dx, self.rect.bottom + dy),
            (self.rect.right + dx, self.rect.bottom + dy),
        ]

        for x, y in corners:
            # Check if the tile is a wall
            if self.game.map.is_wall(x, y):
                return True
        return False


class Pathfinder:
    def __init__(self, game, x, y, sprite):
        self.game = game
        self.sprite = sprite
        self.rect = self.sprite.rect
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

    def get_path(self, start_pos, end_pos):
        # Create a matrix of 1s and 0s for pathfinding for the current map
        matrix = []
        for y in range(self.game.map.tiled_map.height):
            row = []
            for x in range(self.game.map.tiled_map.width):
                pixel_x = x * self.game.TILE_SIZE + self.game.TILE_SIZE // 2
                pixel_y = y * self.game.TILE_SIZE + self.game.TILE_SIZE // 2
                if self.game.map.is_wall(pixel_x, pixel_y):
                    row.append(0)
                else:
                    row.append(1)
            matrix.append(row)
        
        grid = Grid(matrix=matrix)

        # Convert pixel coordinates to grid coordinates
        start_x, start_y = (
            int(start_pos[0] // self.game.TILE_SIZE),
            int(start_pos[1] // self.game.TILE_SIZE),
        )
        end_x, end_y = (
            int(end_pos[0] // self.game.TILE_SIZE),
            int(end_pos[1] // self.game.TILE_SIZE),
        )
        
        # Ensure start and end nodes are within grid bounds
        if not (0 <= start_x < grid.width and 0 <= start_y < grid.height):
            return []
        if not (0 <= end_x < grid.width and 0 <= end_y < grid.height):
            return []

        start_node = grid.node(start_x, start_y)
        end_node = grid.node(end_x, end_y)
        
        # If start or end nodes are not walkable, return empty path
        if not grid.walkable(start_node.x, start_node.y) or not grid.walkable(end_node.x, end_node.y):
             return []

        grid.cleanup()
        path, runs = self.finder.find_path(start_node, end_node, grid)

        # Convert grid path back to pixel coordinates (centers of tiles)
        pixel_path = []
        for node in path:
            pixel_path.append(
                (
                    node.x * self.game.TILE_SIZE + self.game.TILE_SIZE // 2,
                    node.y * self.game.TILE_SIZE + self.game.TILE_SIZE // 2,
                )
            )
        return pixel_path
