"""Tests for pipeline.schema module."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from pipeline.schema import AnimeEntry, LastUpdated, Schedule


class TestAnimeEntry:
    """Tests for AnimeEntry Pydantic model."""

    def test_valid_entry(self) -> None:
        """Accepts a fully valid AnimeEntry."""
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
        assert entry.id == 12345
        assert entry.title == "Solo Leveling"
        assert entry.genres == ["Action", "Fantasy"]

    def test_optional_score_null(self) -> None:
        """Accepts None for optional score field."""
        entry = AnimeEntry(
            id=1,
            title="Test",
            title_en="Test",
            cover="",
            genres=[],
            score=None,
            airing_day="monday",
            airing_time="09:00",
            next_episode=1,
            total_episodes=None,
            next_air_utc=datetime.now(timezone.utc),
            mal_url="https://myanimelist.net/anime/1",
        )
        assert entry.score is None
        assert entry.total_episodes is None

    def test_rejects_missing_id(self) -> None:
        """Rejects entry without required id field."""
        with pytest.raises(ValidationError):
            AnimeEntry(
                title="Test",
                title_en="Test",
                cover="",
                genres=[],
                airing_day="monday",
                airing_time="09:00",
                next_episode=1,
                next_air_utc=datetime.now(timezone.utc),
                mal_url="",
            )  # type: ignore[call-arg]

    def test_rejects_missing_title(self) -> None:
        """Rejects entry without required title field."""
        with pytest.raises(ValidationError):
            AnimeEntry(
                id=1,
                title_en="Test",
                cover="",
                genres=[],
                airing_day="monday",
                airing_time="09:00",
                next_episode=1,
                next_air_utc=datetime.now(timezone.utc),
                mal_url="",
            )  # type: ignore[call-arg]

    def test_rejects_wrong_type_for_id(self) -> None:
        """Rejects non-integer id."""
        with pytest.raises(ValidationError):
            AnimeEntry(
                id="not-a-number",  # type: ignore[arg-type]
                title="Test",
                title_en="Test",
                cover="",
                genres=[],
                airing_day="monday",
                airing_time="09:00",
                next_episode=1,
                next_air_utc=datetime.now(timezone.utc),
                mal_url="",
            )


class TestSchedule:
    """Tests for Schedule Pydantic model."""

    def test_valid_schedule(self) -> None:
        """Accepts a valid schedule with empty week."""
        schedule = Schedule(
            generated_at=datetime.now(timezone.utc),
            week={"monday": [], "tuesday": []},
        )
        assert isinstance(schedule.generated_at, datetime)
        assert "monday" in schedule.week

    def test_schedule_with_entries(self) -> None:
        """Accepts a schedule containing anime entries."""
        entry = AnimeEntry(
            id=1,
            title="Test",
            title_en="Test",
            cover="",
            genres=[],
            airing_day="monday",
            airing_time="09:00",
            next_episode=1,
            next_air_utc=datetime.now(timezone.utc),
            mal_url="",
        )
        schedule = Schedule(
            generated_at=datetime.now(timezone.utc),
            week={"monday": [entry]},
        )
        assert len(schedule.week["monday"]) == 1


class TestLastUpdated:
    """Tests for LastUpdated Pydantic model."""

    def test_valid(self) -> None:
        """Accepts valid last_updated metadata."""
        meta = LastUpdated(
            utc=datetime.now(timezone.utc),
            source="jikan-v4",
        )
        assert meta.source == "jikan-v4"

    def test_default_source(self) -> None:
        """Uses default source when not specified."""
        meta = LastUpdated(utc=datetime.now(timezone.utc))
        assert meta.source == "jikan-v4"
