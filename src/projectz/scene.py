import abc


class Scene(abc.ABC):
    @abc.abstractproperty
    def name(self) -> str: ...

    @abc.abstractmethod
    def update(self, dt: int) -> None: ...

    @abc.abstractmethod
    def draw(self) -> None: ...
