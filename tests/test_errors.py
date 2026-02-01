from projectz import errors


def test_game_exit_error_initialization() -> None:
    """
    Tests that GameExitError can be instantiated with a message.
    """
    error_message = "This is a custom error message."
    error = errors.GameExitError(error_message)
    assert str(error) == error_message
    assert error.reason == "quit"
