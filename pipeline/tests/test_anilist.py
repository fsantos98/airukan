"""Tests for pipeline.anilist module."""

from unittest.mock import MagicMock, patch

import pytest

from pipeline.anilist import BATCH_SIZE, fetch_anilist_airing


def _make_anilist_response(media: list[dict], has_next: bool = False) -> dict:
    """Create a mock AniList GraphQL response."""
    return {
        "data": {
            "Page": {
                "pageInfo": {"hasNextPage": has_next},
                "media": media,
            }
        }
    }


class TestFetchAnilistAiring:
    """Tests for fetch_anilist_airing."""

    def test_empty_ids(self) -> None:
        """Should return empty dict for no IDs."""
        assert fetch_anilist_airing([]) == {}

    @patch("pipeline.anilist.requests.post")
    def test_basic_fetch(self, mock_post: MagicMock) -> None:
        """Should return airing data mapped by MAL ID."""
        response = _make_anilist_response([
            {
                "idMal": 12345,
                "nextAiringEpisode": {
                    "episode": 5,
                    "airingAt": 1741996800,
                    "timeUntilAiring": 3600,
                },
            },
            {
                "idMal": 67890,
                "nextAiringEpisode": None,
            },
        ])
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = response
        mock_resp.headers = {"X-RateLimit-Remaining": "80"}
        mock_post.return_value = mock_resp

        result = fetch_anilist_airing([12345, 67890])
        assert 12345 in result
        assert result[12345]["episode"] == 5
        assert 67890 not in result  # no nextAiringEpisode

    @patch("pipeline.anilist.requests.post")
    def test_deduplicates_ids(self, mock_post: MagicMock) -> None:
        """Should deduplicate MAL IDs before querying."""
        response = _make_anilist_response([])
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = response
        mock_resp.headers = {"X-RateLimit-Remaining": "80"}
        mock_post.return_value = mock_resp

        fetch_anilist_airing([1, 1, 1, 2, 2])
        # Only one batch call since 2 unique IDs < BATCH_SIZE
        assert mock_post.call_count == 1

    @patch("pipeline.anilist.time.sleep")
    @patch("pipeline.anilist.requests.post")
    def test_rate_limit_retry(self, mock_post: MagicMock, mock_sleep: MagicMock) -> None:
        """Should retry on 429 with Retry-After delay."""
        rate_limited = MagicMock()
        rate_limited.status_code = 429
        rate_limited.headers = {"Retry-After": "2"}
        rate_limited.raise_for_status.side_effect = None

        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.json.return_value = _make_anilist_response([])
        ok_response.headers = {"X-RateLimit-Remaining": "80"}

        mock_post.side_effect = [rate_limited, ok_response]

        fetch_anilist_airing([1])
        mock_sleep.assert_any_call(2)
