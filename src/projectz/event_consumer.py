import abc
import pygame


class EventConsumer(abc.ABC):
    """
    An abstract base class for event consumers.
    """

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """
        Handles a pygame event.

        Args:
            event: The event to handle.
        """
        ...
