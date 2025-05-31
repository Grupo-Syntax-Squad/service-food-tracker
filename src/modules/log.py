import logging
from typing import Any


class Log:
    def __init__(
        self,
        name: str = __name__,
        level: int = logging.INFO,
        log_file: str | None = "service_food_tracker.log",
    ):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._log_file = log_file

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

            if self._log_file:
                file_handler = logging.FileHandler(self._log_file, mode="a")
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)

    def debug(self, message: Any, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs, stacklevel=2)

    def info(self, message: Any, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs, stacklevel=2)

    def warning(self, message: Any, *args, **kwargs) -> None:
        self._logger.warning(message, *args, **kwargs, stacklevel=2)

    def error(self, message: Any, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs, stacklevel=2)

    def critical(self, message: Any, *args, **kwargs) -> None:
        self._logger.critical(message, *args, **kwargs, stacklevel=2)
