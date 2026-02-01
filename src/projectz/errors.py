class GameExitError(Exception):
    def __init__(self, message: str, reason: str = "quit"):
        super().__init__(message)
        self.reason = reason
