"""Tests for pipeline.transform module."""

from datetime import datetime, timezone

import pytest

from pipeline.schema import AnimeEntry
from pipeline.transform import (
    _compute_next_air_utc,
    _extract_genres,
    _normalize_day,
    _parse_broadcast_time,
    transform_anime,
    transform_schedule,
)


class TestExtractGenres:
    """Tests for _extract_genres."""

    def test_extracts_genre_names(self) -> None:
        """Should extract name fields from genre dicts."""
        raw = [{"name": "Action"}, {"name": "Fantasy"}]
        assert _extract_genres(raw) == ["Action", "Fantasy"]

    def test_skips_empty_names(self) -> None:
        """Should skip entries with empty or missing name fields."""
        raw = [{"name": "Action"}, {"name": ""}, {"other": "x"}]
        assert _extract_genres(raw) == ["Action"]

    def test_empty_list(self) -> None:
        """Should return empty list for empty input."""
        assert _extract_genres([]) == []


class TestParseBroadcastTime:
    """Tests for _parse_broadcast_time."""

    def test_valid_broadcast(self) -> None:
        """Should return the time string."""
        assert _parse_broadcast_time({"time": "23:00"}) == "23:00"

    def test_missing_time(self) -> None:
        """Should return 'Unknown' when time key is missing."""
        assert _parse_broadcast_time({"day": "Saturday"}) == "Unknown"

    def test_none_broadcast(self) -> None:
        """Should return 'Unknown' for None input."""
        assert _parse_broadcast_time(None) == "Unknown"


class TestNormalizeDay:
    """Tests for _normalize_day."""

    def test_normal_day(self) -> None:
        """Should lowercase a valid day."""
        assert _normalize_day("Monday") == "monday"

    def test_strips_whitespace(self) -> None:
        """Should strip leading/trailing whitespace."""
        assert _normalize_day("  saturday  ") == "saturday"

    def test_invalid_day(self) -> None:
        """Should return 'unknown' for invalid day strings."""
        assert _normalize_day("notaday") == "unknown"

    def test_none(self) -> None:
        """Should return 'unknown' for None."""
        assert _normalize_day(None) == "unknown"

    def test_empty_string(self) -> None:
        """Should return 'unknown' for empty string."""
        assert _normalize_day("") == "unknown"


class TestComputeNextAirUtc:
    """Tests for _compute_next_air_utc."""

    def test_returns_datetime(self) -> None:
        """Should return a timezone-aware datetime."""
        result = _compute_next_air_utc("saturday", "23:00")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_unknown_time_returns_now(self) -> None:
        """Should return approximately now for unknown time."""
        before = datetime.now(timezone.utc)
        result = _compute_next_air_utc("saturday", "Unknown")
        after = datetime.now(timezone.utc)
        assert before <= result <= after

    def test_invalid_day_returns_now(self) -> None:
        """Should return approximately now for invalid day."""
        before = datetime.now(timezone.utc)
        result = _compute_next_air_utc("invalid", "23:00")
        after = datetime.now(timezone.utc)
        assert before <= result <= after


def _make_raw_anime(
    mal_id: int = 12345,
    title: str = "Test Anime",
    title_en: str | None = "Test Anime EN",
    day: str = "Saturdays",
    time: str = "23:00",
    score: float | None = 8.5,
    episodes: int | None = 12,
) -> dict:
    """Create a raw Jikan anime dict for testing."""
    return {
        "mal_id": mal_id,
        "title": title,
        "title_english": title_en,
        "images": {
            "jpg": {
                "image_url": "https://cdn.example.com/small.jpg",
                "large_image_url": "https://cdn.example.com/large.jpg",
            }
        },
        "genres": [{"name": "Action"}, {"name": "Fantasy"}],
        "score": score,
        "broadcast": {"day": day, "time": time},
        "episodes": episodes,
        "status": "Currently Airing",
        "url": f"https://myanimelist.net/anime/{mal_id}",
    }


class TestTransformAnime:
    """Tests for transform_anime."""

    def test_happy_path(self) -> None:
        """Should transform a complete raw anime dict into an AnimeEntry."""
        raw = _make_raw_anime()
        result = transform_anime(raw)
        assert result is not None
        assert result.id == 12345
        assert result.title == "Test Anime"
        assert result.title_en == "Test Anime EN"
        assert result.cover == "https://cdn.example.com/large.jpg"
        assert result.genres == ["Action", "Fantasy"]
        assert result.score == 8.5
        assert result.airing_day == "saturday"
        assert result.airing_time == "23:00"
        assert result.total_episodes == 12
        assert result.mal_url == "https://myanimelist.net/anime/12345"

    def test_missing_title_returns_none(self) -> None:
        """Should return None when title is missing."""
        raw = _make_raw_anime()
        del raw["title"]
        assert transform_anime(raw) is None

    def test_missing_mal_id_returns_none(self) -> None:
        """Should return None when mal_id is missing."""
        raw = _make_raw_anime()
        del raw["mal_id"]
        assert transform_anime(raw) is None

    def test_missing_english_title_falls_back(self) -> None:
        """Should use main title when English title is missing."""
        raw = _make_raw_anime(title_en=None)
        result = transform_anime(raw)
        assert result is not None
        assert result.title_en == "Test Anime"

    def test_null_score(self) -> None:
        """Should accept null score."""
        raw = _make_raw_anime(score=None)
        result = transform_anime(raw)
        assert result is not None
        assert result.score is None

    def test_null_episodes(self) -> None:
        """Should accept null episodes."""
        raw = _make_raw_anime(episodes=None)
        result = transform_anime(raw)
        assert result is not None
        assert result.total_episodes is None

    def test_missing_broadcast(self) -> None:
        """Should handle missing broadcast info gracefully."""
        raw = _make_raw_anime()
        del raw["broadcast"]
        result = transform_anime(raw)
        assert result is not None
        assert result.airing_day == "unknown"
        assert result.airing_time == "Unknown"


class TestTransformAnimeWithAnilist:
    """Tests for transform_anime with AniList airing data."""

    def test_uses_anilist_episode(self) -> None:
        """Should use AniList episode number when provided."""
        raw = _make_raw_anime(episodes=12)
        anilist = {"episode": 5, "airingAt": 1741996800, "timeUntilAiring": 3600}
        result = transform_anime(raw, anilist_airing=anilist)
        assert result is not None
        assert result.next_episode == 5

    def test_uses_anilist_airing_time(self) -> None:
        """Should use AniList airingAt for next_air_utc."""
        raw = _make_raw_anime()
        anilist = {"episode": 3, "airingAt": 1741996800, "timeUntilAiring": 3600}
        result = transform_anime(raw, anilist_airing=anilist)
        assert result is not None
        assert result.next_air_utc == datetime(2025, 3, 15, 0, 0, 0, tzinfo=timezone.utc)

    def test_falls_back_without_anilist(self) -> None:
        """Should use Jikan-based logic when no AniList data."""
        raw = _make_raw_anime(episodes=12)
        result = transform_anime(raw, anilist_airing=None)
        assert result is not None
        assert result.next_episode == 13  # episodes + 1

    def test_falls_back_without_airing_at(self) -> None:
        """Should compute next_air_utc from Jikan when airingAt is missing."""
        raw = _make_raw_anime()
        anilist = {"episode": 5}
        result = transform_anime(raw, anilist_airing=anilist)
        assert result is not None
        assert result.next_episode == 5
        assert result.next_air_utc.tzinfo is not None


class TestTransformSchedule:
    """Tests for transform_schedule."""

    def test_groups_by_day(self) -> None:
        """Should return entries grouped by day."""
        raw_by_day = {
            "monday": [_make_raw_anime(mal_id=1, day="Mondays")],
            "saturday": [_make_raw_anime(mal_id=2, day="Saturdays")],
        }
        result = transform_schedule(raw_by_day)
        assert len(result["monday"]) == 1
        assert len(result["saturday"]) == 1
        assert result["monday"][0].id == 1
        assert result["saturday"][0].id == 2

    def test_empty_days(self) -> None:
        """Should return empty lists for days with no anime."""
        result = transform_schedule({})
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            assert result[day] == []

    def test_skips_invalid_entries(self) -> None:
        """Should skip entries that fail transformation."""
        raw_by_day = {
            "monday": [
                _make_raw_anime(mal_id=1),
                {"invalid": "data"},  # missing required fields
            ],
        }
        result = transform_schedule(raw_by_day)
        assert len(result["monday"]) == 1
