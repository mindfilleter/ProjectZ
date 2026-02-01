from unittest import mock

from projectz import errors
from projectz import game


def test_game_initialization() -> None:
    """
    Tests that the Game class initializes with an empty scenes dictionary.
    """
    g = game.Game()
    assert g.scenes == {}


def test_main_loop_exit() -> None:
    """
    Tests that the main_loop exits gracefully on GameExitError.
    """
    g = game.Game()
    with mock.patch("time.sleep", side_effect=errors.GameExitError("Test Exit")):
        g.main_loop()
