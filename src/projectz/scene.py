import abc

from pygame import event


class Scene(abc.ABC):
    @abc.abstractproperty
    def name(self) -> str: ...

    @abc.abstractmethod
    def update(self, dt: int) -> None: ...

    @abc.abstractmethod
    def draw(self) -> None: ...

    @abc.abstractmethod
    def handle_event(self, e: event.Event) -> None: ...
