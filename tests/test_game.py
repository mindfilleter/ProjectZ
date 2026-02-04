from unittest import mock

import pytest
from pygame import time

from projectz.core import errors
from projectz.core import game
from projectz.core import scene


def test_game_initialization() -> None:
    """
    Tests that the Game class initializes with an empty scenes dictionary.
    """
    clock = time.Clock()
    g = game.Game(clock)
    assert g.scenes == []


def test_main_loop_exit() -> None:
    """
    Tests that the main_loop exits gracefully on GameExitError.
    """
    clock = mock.Mock(spec=time.Clock)
    g = game.Game(clock)

    mock_scene = mock.Mock(spec=scene.Scene)
    mock_scene.update.side_effect = errors.GameExitError("Test Exit")
    g.scenes.append(mock_scene)
    g.set_current_scene(mock_scene.__class__)

    g.main_loop()

    mock_scene.update.assert_called_once()


def test_scene_not_found() -> None:
    g = game.Game(mock.Mock(spec=time.Clock))

    with pytest.raises(ValueError, match="^Scene not found: .+"):
        g.set_current_scene(mock.Mock(spec=scene.Scene))


def test_set_current_scene() -> None:
    """
    Tests that the `set_current_scene` method correctly sets the next scene.
    """
    clock = mock.Mock(spec=time.Clock)
    g = game.Game(clock)

    mock_scene = mock.Mock(spec=scene.Scene)
    g.scenes.append(mock_scene)
    g.set_current_scene(mock_scene.__class__)

    assert g._next_scene is mock_scene
