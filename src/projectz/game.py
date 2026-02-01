import logging
from typing import List
from typing import Optional
from typing import Type

from pygame import event
from pygame import time

from projectz import errors
from projectz import scene

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, clock: time.Clock) -> None:
        self.scenes: List[scene.Scene] = []
        self.current_scene: Optional[scene.Scene] = None
        self._next_scene: Optional[scene.Scene] = None
        self.clock = clock

    def set_current_scene(self, scene_cls: Type[scene.Scene]) -> None:
        for s in self.scenes:
            if isinstance(s, scene_cls):
                self._next_scene = s
                if self.current_scene is None:
                    self.current_scene = s
                return
        raise ValueError(f"Scene not found:  {str(scene_cls)}")

    def main_loop(self) -> None:
        try:
            while self.current_scene is not None:
                self.current_scene.update(self.clock.tick(60))
                for e in event.get():
                    self.current_scene.handle_event(e)

                if self._next_scene is not None and self.current_scene is not self._next_scene:
                    self.current_scene = self._next_scene
        except errors.GameExitError as e:
            logger.error("Game Exit: %s", e, exc_info=False)
