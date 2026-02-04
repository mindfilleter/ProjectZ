from unittest import mock

from projectz import bootstrap


@mock.patch("pygame.init")
@mock.patch("pygame.display.set_mode")
@mock.patch("pygame.display.set_caption")
def test_init_pygame(
    mock_set_caption: mock.Mock, mock_set_mode: mock.Mock, mock_init: mock.Mock
) -> None:
    """
    Tests that the pygame initialization function calls the correct pygame functions.
    """
    bootstrap.init_pygame()
    mock_init.assert_called_once()
    mock_set_mode.assert_called_once_with((800, 600))
    mock_set_caption.assert_called_once_with("ProjectZ")


@mock.patch("pygame.time.Clock")
@mock.patch("projectz.core.game.Game")
@mock.patch("projectz.title.TitleScene")
def test_create_game(
    mock_title_scene: mock.Mock, mock_game: mock.Mock, mock_clock: mock.Mock
) -> None:
    """
    Tests that the game creation function creates a game and adds the title scene.
    """
    g = bootstrap.create_game(mock_clock)
    mock_game.assert_called_once_with(mock_clock)
    mock_title_scene.assert_called_once()
    g = mock_game.return_value
    g.__setitem__.assert_called_once_with(
        mock_title_scene.return_value.name, mock_title_scene.return_value
    )
    g.set_current_scene.assert_called_once_with(mock_title_scene)
