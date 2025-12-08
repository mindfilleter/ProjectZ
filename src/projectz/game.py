from importlib import resources
import pytmx
import pygame
from pygame import display
from pygame import event
from pygame import time
from pygame import sprite

# --- Map Helper Functions (Your selected code) ---


def load_map(map_name):
    """Loads a TMX map and returns a TiledMap object."""
    with resources.path("projectz.assets", map_name) as map_path:
        return pytmx.load_pygame(map_path, pixelalpha=True)


def render_layer(surface, tiled_map, layer_name):
    """Renders a specific layer of the TMX map on the given surface."""
    try:
        layer = tiled_map.get_layer_by_name(layer_name)
    except ValueError:
        print(f"Warning: '{layer_name}' layer not found in map.")
        return

    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            tile = tiled_map.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(
                    tile,
                    (x * tiled_map.tilewidth, y * tiled_map.tileheight),
                )


def get_collision_rects(tiled_map):
    """
    Reads the object layer called 'walkable' and returns a list of Pygame Rects.
    """
    collision_rects = []

    # 1. Try to find the layer named "walkable" in the map data.
    try:
        walkable_layer = tiled_map.get_layer_by_name("walkable")
    except ValueError:
        print("Warning: 'walkable' object layer not found in map.")
        return collision_rects

    # 2. Loop through every object the artist drew on that layer.
    for obj in walkable_layer:
        # 3. Create a Pygame Rect object.
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        collision_rects.append(rect)

    return collision_rects


# --- Pygame Setup ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Game Classes ---


class Game:

    TARGET_FPS = 60

    def __init__(self, config):
        self.config = config
        self.clock = time.Clock()
        self.running = True
        self.player = Player()

        # NEW: These will hold our map and the list of collision rectangles!
        self.tiled_map = None
        self.collision_rects = []

    def start(self):

        # FIX 1: Load the map ONCE and store the correct PyTMX object in self.tiled_map
        self.tiled_map = load_map("map.tmx")

        # FIX 2: Generate the list of collision rects ONCE from the correct map object
        self.collision_rects = get_collision_rects(self.tiled_map)

        screen = display.get_surface()

        # This while loop is like the Scratch 'forever' block!
        while self.running:
            self.clock.tick(Game.TARGET_FPS)

            for pygame_event in event.get():
                if pygame_event.type == pygame.QUIT:
                    self.running = False
                self.player.handle_event(pygame_event)

            # FIX 3: Now we pass the simple list of collision Rects to the player!
            self.player.update(self.collision_rects)

            # Drawing Step:
            screen.fill((0, 0, 0))
            # Use the stored map object for rendering
            render_layer(screen, self.tiled_map, "ground")
            self.player.draw(screen)
            render_layer(screen, self.tiled_map, "foreground")
            pygame.display.flip()


class Player(sprite.Sprite):
    def __init__(self, *groups):
        sprite.Sprite.__init__(self, *groups)
        self.pos = pygame.math.Vector2(16, 16)
        self.vel = pygame.math.Vector2(0, 0)
        self.spd = 4
        self.friction = 0.5
        self.rect = pygame.rect.Rect(self.pos.x, self.pos.y, 16, 16)
        self.move_dir = []

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
        # Draw a red rectangle (our player sprite!)
        pygame.draw.rect(surface, (255, 0, 0), self.rect)
