from src.env import LOGGER_CLIO


class Logger:
    """Class in charge of managing the logging"""

    def __init__(self, log_type: str = 'cli') -> None:
        self.log_type = log_type

    def _cli_log(self, text: str) -> None:
        print(text)

    def log(self, text: str) -> None:
        if self.log_type == 'cli' and LOGGER_CLIO:
            self._cli_log(text=text)
