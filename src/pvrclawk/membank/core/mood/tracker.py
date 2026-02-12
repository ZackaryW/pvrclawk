import json
from pathlib import Path

from pvrclawk.membank.models.config import AppConfig


class MoodTracker:
    def __init__(self, mood_file: Path, config: AppConfig):
        self.mood_file = mood_file
        self.config = config

    def _read(self) -> dict[str, float]:
        if not self.mood_file.exists():
            return {}
        return json.loads(self.mood_file.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, float]) -> None:
        self.mood_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get(self, tag: str) -> float:
        data = self._read()
        return float(data.get(tag, self.config.mood.default))

    def report(self, tag: str, value: float) -> float:
        data = self._read()
        old = float(data.get(tag, self.config.mood.default))
        alpha = self.config.mood.smoothing
        new_value = old * (1 - alpha) + value * alpha
        data[tag] = new_value
        self._write(data)
        return new_value
