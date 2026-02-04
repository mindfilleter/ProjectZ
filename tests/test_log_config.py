import io
import logging
from typing import Any
from typing import Dict
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import structlog
from pygame import time

from projectz.core import game
from projectz.core import log_config


@pytest.fixture
def mock_clock() -> time.Clock:
    """Fixture to create a mock pygame Clock."""
    clock = MagicMock(spec=time.Clock)
    clock.get_fps.return_value = 60.0
    return clock


@pytest.fixture
def mock_game(mock_clock: time.Clock) -> game.Game:
    """Fixture to create a mock Game object."""
    g = MagicMock(spec=game.Game)
    g.frame_count = 100
    return g


@pytest.fixture(autouse=True)
def isolated_logging() -> Generator[None, None, None]:
    """Fixture to ensure logging is isolated for each test."""
    structlog.reset_defaults()
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    root_logger.handlers = []
    yield
    structlog.reset_defaults()
    root_logger.handlers = original_handlers


def test_pygame_context_processor(mock_clock: time.Clock, mock_game: game.Game) -> None:
    # Arrange
    processor = log_config.get_pygame_context_processor(mock_clock, mock_game)
    event_dict: Dict[str, Any] = {}

    with patch("pygame.time.get_ticks", return_value=12345):
        # Act
        processed_dict = processor(None, "", event_dict)

    # Assert
    assert processed_dict["frame"] == 100
    assert processed_dict["elapsed_sec"] == 12.345
    assert processed_dict["fps"] == 60.0


def test_setup_logging_produces_structured_logs(
    mock_clock: time.Clock, mock_game: game.Game
) -> None:
    # Arrange
    log_capture_string = io.StringIO()
    original_handler = logging.getLogger().handlers
    logging.getLogger().handlers = [logging.StreamHandler(log_capture_string)]

    class NonColorConsoleRenderer(structlog.dev.ConsoleRenderer):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(colors=False, **kwargs)

    with patch("structlog.dev.ConsoleRenderer", NonColorConsoleRenderer):
        # Act
        log_config.setup_logging(mock_clock, mock_game)
        logger = structlog.get_logger("test_logger")
        with patch("pygame.time.get_ticks", return_value=54321):
            logger.info("A test event", key="value")

    # Assert
    log_output = log_capture_string.getvalue()
    assert "A test event" in log_output
    assert "key=value" in log_output
    assert "test_logger" in log_output
    assert "frame=100" in log_output
    assert "elapsed_sec=54.321" in log_output
    assert "fps=60.0" in log_output

    logging.getLogger().handlers = original_handler
