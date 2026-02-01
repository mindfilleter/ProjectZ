import os
from typing import Generator

import pygame
import pytest


@pytest.fixture(scope="function")
def pygame_session() -> Generator[None, None, None]:
    """
    Initializes a headless pygame-ce session for testing.

    This fixture sets the SDL_VIDEODRIVER to 'dummy' to prevent
    a display from being created, initializes pygame, yields
    to the test, and then quits pygame.
    """
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()
