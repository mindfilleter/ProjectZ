import logging
import time
from typing import Dict

from projectz import errors
from projectz import scene

logger = logging.getLogger(__name__)


class Game:
    def __init__(self) -> None:
        self.scenes: Dict[str, scene.Scene] = {}

    def main_loop(self) -> None:
        try:
            while True:
                time.sleep(0.01)
        except errors.GameExitError as e:
            logger.error("Game Exit: %s", e, exc_info=False)
