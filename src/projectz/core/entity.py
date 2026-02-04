import abc
from collections.abc import Mapping
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

import structlog
from pygame import event
from pygame import sprite

logger = structlog.get_logger(__name__)
T = TypeVar("T", bound="Component")


class Component(abc.ABC):
    def __init__(self) -> None:
        self.owner: Optional["Entity"] = None

    @abc.abstractmethod
    def update(self, dt: int) -> None: ...

    @abc.abstractmethod
    def handle_event(self, pygame_event: event.Event) -> bool:
        """
        Returns True if the event is consumed, False otherwise.
        """
        ...


class Entity(sprite.Sprite, Mapping[Type[Component], Component]):
    def __init__(
        self, *groups: sprite.AbstractGroup["Entity"], components: Optional[List[Component]] = None
    ):
        super().__init__(*groups)
        # super(Mapping, self).__init__()

        self._components: List[Component] = []

        logger.debug("Initializing Entity %s", self)

        if components:
            self.add_components(*components)

    def add_components(self, *components: Component) -> None:
        for component in components:
            component.owner = self
            self._components.append(component)
            logger.debug("Added %s to %s", type(component).__name__, self)

    def __getitem__(self, key: Type[T]) -> T:
        for component in self._components:
            if isinstance(component, key):
                return component
        raise KeyError(f"Component of type {key.__name__} not found on {self}")

    def __iter__(self) -> Iterator[Type[Component]]:
        for component in self._components:
            yield type(component)

    def __len__(self) -> int:
        return len(self._components)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, type):
            return False
        return any(isinstance(c, key) for c in self._components)

    def __eq__(self, other: object) -> bool:
        return object.__eq__(self, other)

    def __hash__(self) -> int:
        return object.__hash__(self)

    def update(self, dt: int) -> None:
        for component in self._components:
            component.update(dt)

    def handle_event(self, pygame_event: event.Event) -> None:
        for component in self._components:
            if component.handle_event(pygame_event):
                logger.debug(
                    "Event %s consumed by %s on %s", pygame_event, type(component).__name__, self
                )
                return
