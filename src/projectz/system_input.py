import pygame

from projectz.event_consumer import EventConsumer


class SystemEventConsumer(EventConsumer):
    """
    Handles system-level events.
    """



    def __init__(self, game):
        """
        Initializes the system event consumer.

        Args:
            game: The game instance.
        """
        self.game = game

    def handle_event(self, event: pygame.event.Event):
        """
        Handles a pygame event.

        Args:
            event: The event to handle.
        """
        if event.type == pygame.QUIT:
            self.game.running = False
