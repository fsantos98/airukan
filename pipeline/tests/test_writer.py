"""Tests for pipeline.writer module."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from pipeline.schema import AnimeEntry
from pipeline.writer import write_last_updated, write_raw_json, write_schedule


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    """Return a temporary directory to use as data output."""
    return tmp_path / "data"


@pytest.fixture()
def sample_week() -> dict[str, list[AnimeEntry]]:
    """Return a sample week with one entry."""
    entry = AnimeEntry(
        id=12345,
        title="Solo Leveling",
        title_en="Solo Leveling",
        cover="https://cdn.example.com/cover.jpg",
        genres=["Action", "Fantasy"],
        score=8.7,
        airing_day="saturday",
        airing_time="23:00",
        next_episode=8,
        total_episodes=12,
        next_air_utc=datetime(2025, 3, 1, 14, 0, 0, tzinfo=timezone.utc),
        mal_url="https://myanimelist.net/anime/12345",
    )
    return {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [entry],
        "sunday": [],
    }


class TestWriteSchedule:
    """Tests for write_schedule."""

    def test_creates_file(
        self, tmp_data_dir: Path, sample_week: dict[str, list[AnimeEntry]]
    ) -> None:
        """Creates schedule.json in the data directory."""
        path = write_schedule(sample_week, data_dir=tmp_data_dir)
        assert path.exists()
        assert path.name == "schedule.json"

    def test_valid_json(
        self, tmp_data_dir: Path, sample_week: dict[str, list[AnimeEntry]]
    ) -> None:
        """Written file contains valid JSON."""
        path = write_schedule(sample_week, data_dir=tmp_data_dir)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "generated_at" in data
        assert "week" in data

    def test_contains_entries(
        self, tmp_data_dir: Path, sample_week: dict[str, list[AnimeEntry]]
    ) -> None:
        """Written schedule contains the anime entries."""
        path = write_schedule(sample_week, data_dir=tmp_data_dir)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["week"]["saturday"]) == 1
        assert data["week"]["saturday"][0]["title"] == "Solo Leveling"

    def test_creates_directory(
        self, tmp_data_dir: Path, sample_week: dict[str, list[AnimeEntry]]
    ) -> None:
        """Creates the data directory if it doesn't exist."""
        assert not tmp_data_dir.exists()
        write_schedule(sample_week, data_dir=tmp_data_dir)
        assert tmp_data_dir.exists()


class TestWriteLastUpdated:
    """Tests for write_last_updated."""

    def test_creates_file(self, tmp_data_dir: Path) -> None:
        """Creates last_updated.json in the data directory."""
        path = write_last_updated(data_dir=tmp_data_dir)
        assert path.exists()
        assert path.name == "last_updated.json"

    def test_valid_json(self, tmp_data_dir: Path) -> None:
        """Written file contains valid JSON with expected fields."""
        path = write_last_updated(data_dir=tmp_data_dir)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "utc" in data
        assert "source" in data
        assert data["source"] == "jikan-v4+anilist"

    def test_timestamp_is_recent(self, tmp_data_dir: Path) -> None:
        """Written timestamp is close to current time."""
        before = datetime.now(timezone.utc)
        path = write_last_updated(data_dir=tmp_data_dir)
        data = json.loads(path.read_text(encoding="utf-8"))
        timestamp = datetime.fromisoformat(data["utc"])
        assert timestamp >= before


class TestWriteRawJson:
    """Tests for write_raw_json."""

    def test_creates_file(self, tmp_data_dir: Path) -> None:
        """Creates the specified JSON file."""
        path = write_raw_json({"key": "value"}, "test_raw.json", data_dir=tmp_data_dir)
        assert path.exists()
        assert path.name == "test_raw.json"

    def test_valid_json(self, tmp_data_dir: Path) -> None:
        """Written file contains valid JSON matching input."""
        data = {"ids": [1, 2, 3], "nested": {"a": "b"}}
        path = write_raw_json(data, "test_raw.json", data_dir=tmp_data_dir)
        written = json.loads(path.read_text(encoding="utf-8"))
        assert written == data

    def test_creates_directory(self, tmp_data_dir: Path) -> None:
        """Creates the data directory if it doesn't exist."""
        assert not tmp_data_dir.exists()
        write_raw_json({"x": 1}, "test.json", data_dir=tmp_data_dir)
        assert tmp_data_dir.exists()
