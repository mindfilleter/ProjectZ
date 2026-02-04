from unittest import mock

import pytest
from pygame import event

from projectz.core import entity


class MockComponent(entity.Component):
    def update(self, dt: int) -> None:
        pass

    def handle_event(self, pygame_event: event.Event) -> bool:
        return False


class AnotherComponent(entity.Component):
    def update(self, dt: int) -> None:
        pass

    def handle_event(self, pygame_event: event.Event) -> bool:
        return True


class NotInEntity:
    pass


class TestEntity:
    def test_initialization_with_components(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        assert MockComponent in e
        assert component.owner == e

    def test_add_components(self) -> None:
        component = MockComponent()
        e = entity.Entity()
        e.add_components(component)
        assert MockComponent in e
        assert component.owner == e

    def test_getitem(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        assert e[MockComponent] == component

    def test_getitem_not_found(self) -> None:
        e = entity.Entity()
        with pytest.raises(KeyError):
            _ = e[MockComponent]

    def test_iter(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        assert list(iter(e)) == [MockComponent]

    def test_len(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        assert len(e) == 1

    def test_contains(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        assert MockComponent in e
        assert AnotherComponent not in e
        assert NotInEntity not in e  # type: ignore

    def test_update(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        with mock.patch.object(component, "update") as mock_update:
            e.update(100)
            mock_update.assert_called_once_with(100)

    def test_handle_event(self) -> None:
        component = MockComponent()
        e = entity.Entity(components=[component])
        with mock.patch.object(component, "handle_event") as mock_handle_event:
            e.handle_event(event.Event(1))
            mock_handle_event.assert_called_once()

    def test_handle_event_consumed(self) -> None:
        component = AnotherComponent()
        e = entity.Entity(components=[component, MockComponent()])
        with (
            mock.patch.object(component, "handle_event", return_value=True) as mock_handle,
            mock.patch.object(MockComponent, "handle_event") as mock_handle_2,
        ):
            e.handle_event(event.Event(1))
            mock_handle.assert_called_once()
            mock_handle_2.assert_not_called()
