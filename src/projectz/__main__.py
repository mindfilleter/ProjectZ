import pygame

from projectz.bootstrap import init_pygame
from projectz.map import load_map, render_map


def main():
    """The main entry point for the game."""
    screen = init_pygame()
    tiled_map = load_map("map.tmx")
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        render_map(screen, tiled_map)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
