import typing
from unittest import mock

import pygame
import pytest

from projectz import title


@mock.patch("pygame.display.get_surface")
@mock.patch("projectz.assets.get_image")
def test_title_scene_init(
    mock_get_image: mock.Mock, mock_get_surface: mock.Mock, pygame_session: None
) -> None:
    """
    Tests that the title scene initializes correctly.
    """
    mock_get_image.return_value.get_size.return_value = (0, 0)
    ts = title.TitleScene()
    assert ts.name == "title"
    assert len(ts.sprites) == 5


@mock.patch("pygame.display.get_surface")
@mock.patch("pygame.sprite.Group")
@mock.patch("projectz.assets.get_image")
def test_title_scene_draw(
    mock_get_image: mock.Mock,
    mock_sprite_group: mock.Mock,
    mock_get_surface: mock.Mock,
    pygame_session: None,
) -> None:
    """
    Tests that the title scene draws correctly.
    """
    mock_get_image.return_value.get_size.return_value = (0, 0)
    ts = title.TitleScene()
    surface = mock.Mock()
    surface.blits.return_value = []
    with (
        mock.patch("pygame.display.get_surface", return_value=surface),
        mock.patch("pygame.display.flip"),
    ):
        ts.draw()
    surface.fill.assert_called_once_with(pygame.Color(0, 0, 0))
    typing.cast(mock.Mock, ts.sprites).draw.assert_called_once_with(surface)


@mock.patch("pygame.display.get_surface")
@mock.patch("projectz.assets.get_image")
def test_title_scene_handle_event_quit(
    mock_get_image: mock.Mock, mock_get_surface: mock.Mock, pygame_session: None
) -> None:
    """
    Tests that the title scene handles the quit event.
    """
    mock_get_image.return_value.get_size.return_value = (0, 0)
    import pygame

    from projectz.core import errors

    ts = title.TitleScene()
    with pytest.raises(errors.GameExitError):
        ts.handle_event(pygame.event.Event(pygame.QUIT))


@mock.patch("pygame.display.get_surface")
@mock.patch("projectz.assets.get_image")
def test_title_scene_update(
    mock_get_image: mock.Mock, mock_get_surface: mock.Mock, pygame_session: None
) -> None:
    """
    Tests that the title scene update method does nothing.
    """
    mock_get_image.return_value.get_size.return_value = (0, 0)
    ts = title.TitleScene()
    ts.update(0)
