from pathlib import Path

from pvrclawk.utils.json_io import read_json, write_json


def test_write_and_read_json(tmp_path: Path):
    path = tmp_path / "data.json"
    data = {"key": "value", "num": 42}
    write_json(path, data)
    assert path.exists()
    loaded = read_json(path, {})
    assert loaded == data


def test_read_json_missing_file_returns_default(tmp_path: Path):
    path = tmp_path / "missing.json"
    result = read_json(path, {"default": True})
    assert result == {"default": True}


def test_read_json_empty_default(tmp_path: Path):
    path = tmp_path / "nope.json"
    result = read_json(path, [])
    assert result == []


def test_write_json_nested(tmp_path: Path):
    path = tmp_path / "nested.json"
    data = {"a": {"b": [1, 2, 3]}}
    write_json(path, data)
    loaded = read_json(path, {})
    assert loaded["a"]["b"] == [1, 2, 3]
