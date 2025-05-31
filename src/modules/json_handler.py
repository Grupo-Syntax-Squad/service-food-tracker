import json
import os
from typing import Any
from src.schemas.detection import Detection
from src.modules.log import Log


class JSONHandler:
    def __init__(self, file_path: str):
        self._log: Log = Log()
        self._file_path = file_path
        self._content = self._load_file_content()

    def _load_file_content(self) -> list[Any]:
        self._log.info("Trying to load %s file content", self._file_path)
        if not self._file_exists():
            self._log.info("%s file does not exist", self._file_path)
            return []

        try:
            with open(self._file_path, "r") as f:
                content = json.load(f)
                self._log.info("File %s read successfully", self._file_path)
                return content
        except json.JSONDecodeError:
            self._log.error("Error while decoding %s file", self._file_path)
            return []
        except Exception as e:
            self._log.error("Error reading file %s", self._file_path)
            raise e

    def _file_exists(self) -> bool:
        return os.path.exists(self._file_path)

    def save_in_json(self, data: Detection) -> None:
        try:
            json_data = data.model_dump_json()
            self._log.info(
                "Trying to save data %s in the %s file", json_data, self._file_path
            )
            self._content.append(json_data)
            with open(self._file_path, "w") as f:
                json.dump(self._content, f, indent=4)
            self._log.info("Data saved successfully in the %s file", self._file_path)
        except Exception as e:
            self._log.error(
                "Error saving data %s in the file %s: %s", json_data, self._file_path, e
            )
