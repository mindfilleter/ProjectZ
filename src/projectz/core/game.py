import logging
from collections.abc import MutableMapping
from typing import Dict
from typing import Iterator
from typing import Optional
from typing import Type

from pygame import event
from pygame import time

from projectz.core import errors
from projectz.core import scene

logger = logging.getLogger(__name__)


class Game(MutableMapping[str, scene.Scene]):
    def __init__(self, clock: time.Clock) -> None:
        self.scenes: Dict[str, scene.Scene] = {}
        self.current_scene: Optional[scene.Scene] = None
        self._next_scene: Optional[scene.Scene] = None
        self.clock = clock

    def __getitem__(self, key: str) -> scene.Scene:
        return self.scenes[key]

    def __setitem__(self, key: str, value: scene.Scene) -> None:
        self.scenes[key] = value

    def __delitem__(self, key: str) -> None:
        del self.scenes[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.scenes)

    def __len__(self) -> int:
        return len(self.scenes)

    def set_current_scene(self, scene_cls: Type[scene.Scene]) -> None:
        for s in self.scenes.values():
            if isinstance(s, scene_cls):
                self._next_scene = s
                if self.current_scene is None:
                    self.current_scene = s
                return
        raise ValueError(f"Scene not found:  {str(scene_cls)}")

    def main_loop(self) -> None:
        try:
            while self.current_scene is not None:
                for e in event.get():
                    self.current_scene.handle_event(e)
                self.current_scene.update(self.clock.tick(60))
                self.current_scene.draw()
                if self._next_scene is not None and self.current_scene is not self._next_scene:
                    self.current_scene = self._next_scene
        except errors.GameExitError as e:
            logger.error("Game Exit: %s", e, exc_info=False)
