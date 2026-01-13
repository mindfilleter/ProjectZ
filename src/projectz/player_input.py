import pygame

from projectz.event_consumer import EventConsumer
from projectz.input import input_manager
from projectz.player import Player


class PlayerMovementConsumer(EventConsumer):
    """
    Handles player movement events.
    """

    def __init__(self, game, player: Player):
        """
        Initializes the player movement consumer.

        Args:
            player: The player to control.
        """
        self.game = game
        self.player = player

    def handle_event(self, event: pygame.event.Event):
        """
        Handles a pygame event.

        Args:
            event: The event to handle.
        """
        if event.type not in (pygame.KEYDOWN, pygame.KEYUP):
            return

        action = input_manager.get_action(event, self.game.state)
        if action not in ("up", "down", "left", "right"):
            return

        direction = action

        if event.type == pygame.KEYDOWN:
            if direction not in self.player.move_dir:
                self.player.move_dir.append(direction)
        elif event.type == pygame.KEYUP:
            if direction in self.player.move_dir:
                self.player.move_dir.remove(direction)


class PlayerAttackConsumer(EventConsumer):
    """
    Handles player attack events.
    """

    def __init__(self, game, player: Player):
        """
        Initializes the player attack consumer.

        Args:
            player: The player to control.
        """
        self.game = game
        self.player = player

    def handle_event(self, event: pygame.event.Event):
        """
        Handles a pygame event.

        Args:
            event: The event to handle.
        """
        if event.type != pygame.KEYDOWN:
            return

        action = input_manager.get_action(event, self.game.state)
        if action != "talk/attack":
            return

        self.player.attack()
