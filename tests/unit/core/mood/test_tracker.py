from pathlib import Path

from pvrclawk.membank.core.mood.tracker import MoodTracker
from pvrclawk.membank.models.config import AppConfig


def test_mood_default(tmp_path: Path):
    tracker = MoodTracker(tmp_path / "mood.json", AppConfig())
    assert tracker.get("tcp") == 0.5


def test_mood_report_ema(tmp_path: Path):
    tracker = MoodTracker(tmp_path / "mood.json", AppConfig())
    updated = tracker.report("tcp", 1.0)
    assert updated > 0.5
    assert tracker.get("tcp") == updated
