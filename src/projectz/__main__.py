import pygame

from projectz.bootstrap import init_pygame


def main():
    """The main entry point for the game."""
    screen = init_pygame()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()
