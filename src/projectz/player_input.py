import pygame

from projectz.event_consumer import EventConsumer
from projectz.player import Player


class PlayerMovementConsumer(EventConsumer):
    """
    Handles player movement events.
    """

    KEY_DIRECTION_MAP = {
        pygame.K_d: "right",
        pygame.K_a: "left",
        pygame.K_w: "up",
        pygame.K_s: "down",
    }

    def __init__(self, player: Player):
        """
        Initializes the player movement consumer.

        Args:
            player: The player to control.
        """
        self.player = player

    def handle_event(self, event: pygame.event.Event):
        """
        Handles a pygame event.

        Args:
            event: The event to handle.
        """
        if event.type not in (pygame.KEYDOWN, pygame.KEYUP):
            return

        direction = self.KEY_DIRECTION_MAP.get(event.key)
        if not direction:
            return

        if event.type == pygame.KEYDOWN:
            if direction not in self.player.move_dir:
                self.player.move_dir.append(direction)
        elif event.type == pygame.KEYUP:
            if direction in self.player.move_dir:
                self.player.move_dir.remove(direction)
