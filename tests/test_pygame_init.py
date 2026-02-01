from typing import TYPE_CHECKING

import pygame
from pygame import sprite

if TYPE_CHECKING:
    from collections.abc import Generator


def test_pygame_session_initialization(
    pygame_session: "Generator[None, None, None]",
) -> None:
    """
    Tests that the pygame_session fixture initializes pygame successfully.

    This test creates a sprite and a group, adds the sprite to the group,
    and asserts that the display is initialized.
    """
    assert pygame.display.get_init()

    # Create a sprite and a group
    my_sprite: sprite.Sprite = sprite.Sprite()
    my_group: sprite.Group[sprite.Sprite] = sprite.Group()

    # Add the sprite to the group
    my_group.add(my_sprite)

    # Assert that the sprite is in the group
    assert my_sprite in my_group
