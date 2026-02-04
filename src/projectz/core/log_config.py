"""
This module provides a custom logging configuration for Pygame
applications.

It uses structlog to provide structured, extensible logging.
"""

from __future__ import annotations

import logging
import sys
from typing import Any
from typing import Callable
from typing import MutableMapping

import pygame
import structlog
from pygame import time

from projectz.core import game

# Type alias for a structlog processor
Processor = Callable[[Any, str, MutableMapping[str, Any]], MutableMapping[str, Any]]


def get_pygame_context_processor(clock: time.Clock, game_instance: game.Game) -> "Processor":
    """
    Create a structlog processor that injects Pygame state into log records.
    """

    def processor(
        _: Any, __: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        event_dict["frame"] = game_instance.frame_count
        event_dict["elapsed_sec"] = pygame.time.get_ticks() / 1000.0
        event_dict["fps"] = clock.get_fps()
        return event_dict

    return processor


def setup_logging(clock: time.Clock, game_instance: game.Game) -> None:
    """
    Configures structlog to be the primary logging interface.
    """
    # Check if we already have handlers to avoid duplicate logs on
    # reload
    if structlog.is_configured():
        return

    pygame_context_processor = get_pygame_context_processor(clock, game_instance)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-m-%d %H:%M:%S.%f"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            pygame_context_processor,
            structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Get the Root Logger (no name argument)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # The structlog processor chain now handles everything, so we only
    # need a simple handler.
    handler = logging.StreamHandler(sys.stdout)
    root_logger.addHandler(handler)
