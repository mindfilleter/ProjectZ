from typing import Iterator

import pygame
import pytest

from projectz.core import entity
from projectz.ui import button
from projectz.ui import component


@pytest.fixture
def setup_pygame() -> Iterator[None]:
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def test_button(setup_pygame: None) -> entity.Entity:
    """Creates a default button for testing."""
    return button.create_button(
        size=(100, 50),
        text="Test",
        button_id="test_button",
        normal_color=pygame.Color("white"),
        hover_color=pygame.Color("gray"),
        clicked_color=pygame.Color("black"),
    )


def test_button_hover_and_leave(test_button: entity.Entity) -> None:
    """Tests if the button correctly handles hovering and leaving."""
    if not test_button.rect:
        pytest.fail("Button rect should not be None")
    test_button.rect.topleft = (0, 0)

    # Mouse moves over the button
    motion_event_over = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (10, 10)})
    test_button.handle_event(motion_event_over)
    assert test_button[button.ButtonComponent].current_state == button.ButtonState.HOVER

    # Mouse moves off the button
    motion_event_off = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (200, 200)})
    test_button.handle_event(motion_event_off)
    assert test_button[button.ButtonComponent].current_state == button.ButtonState.NORMAL


def test_button_click_sequence(test_button: entity.Entity) -> None:
    """Tests the full click sequence: hover -> click -> release."""
    if not test_button.rect:
        pytest.fail("Button rect should not be None")
    test_button.rect.topleft = (0, 0)
    original_pos = test_button.rect.topleft

    # 1. Hover
    test_button.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": (10, 10)}))
    assert test_button[button.ButtonComponent].current_state == button.ButtonState.HOVER

    # 2. Click down
    test_button.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (10, 10), "button": 1})
    )
    assert test_button[button.ButtonComponent].current_state == button.ButtonState.CLICKED
    shadow_offset = test_button[component.RenderComponent].shadow_offset
    assert test_button.rect.topleft == (
        original_pos[0] + shadow_offset,
        original_pos[1] + shadow_offset,
    )

    # 3. Release
    test_button.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (10, 10), "button": 1})
    )
    assert test_button[button.ButtonComponent].current_state == button.ButtonState.HOVER
    assert test_button.rect.topleft == original_pos

    # Check for the custom event
    events = pygame.event.get()
    assert any(
        event.type == button.BUTTON_CLICKED and event.button_id == "test_button" for event in events
    )


def test_button_no_event_consumption(test_button: entity.Entity) -> None:
    """Tests that events are not consumed when the mouse is not over the button."""
    if not test_button.rect:
        pytest.fail("Button rect should not be None")
    test_button.rect.topleft = (0, 0)

    # Mouse motion not over the button
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (200, 200)})
    consumed = test_button[button.ButtonComponent].handle_event(motion_event)
    assert not consumed

    # Mouse click not over the button
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (200, 200), "button": 1})
    consumed = test_button[button.ButtonComponent].handle_event(click_event)
    assert not consumed
