"""Fetch next-airing episode data from AniList GraphQL API."""

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

ANILIST_URL = "https://graphql.anilist.co"

# AniList rate limit: 30 req/min (degraded) or 90 req/min (normal).
# We check headers and respect Retry-After on 429.
BATCH_SIZE = 50

QUERY = """
query ($idMal_in: [Int], $page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      hasNextPage
    }
    media(type: ANIME, idMal_in: $idMal_in) {
      idMal
      nextAiringEpisode {
        episode
        timeUntilAiring
        airingAt
      }
    }
  }
}
"""


def _request_with_rate_limit(
    variables: dict[str, Any],
    max_retries: int = 3,
) -> dict[str, Any]:
    """Make a single AniList GraphQL request, respecting rate limits.

    Checks X-RateLimit-Remaining and sleeps preemptively when low.
    Retries on 429 using the Retry-After header.
    """
    for attempt in range(max_retries):
        response = requests.post(
            ANILIST_URL,
            json={"query": QUERY, "variables": variables},
            timeout=30,
        )

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(
                "AniList rate limited (429). Retrying after %ds (attempt %d/%d)",
                retry_after, attempt + 1, max_retries,
            )
            time.sleep(retry_after)
            continue

        response.raise_for_status()

        # Preemptive slowdown when nearing the limit
        remaining = int(response.headers.get("X-RateLimit-Remaining", 90))
        if remaining <= 5:
            logger.info("AniList rate limit nearly reached (%d remaining), sleeping 5s", remaining)
            time.sleep(5)

        return response.json()

    raise RuntimeError("AniList API: max retries exceeded due to rate limiting")


def fetch_anilist_airing(mal_ids: list[int]) -> dict[int, dict[str, Any]]:
    """Fetch next-airing episode info from AniList for the given MAL IDs.

    Queries in batches to stay within GraphQL complexity limits.
    Returns a dict mapping mal_id -> airing info dict with keys:
        - episode (int)
        - airingAt (int, unix timestamp)
        - timeUntilAiring (int, seconds)
    Only entries that have a nextAiringEpisode are included.
    """
    if not mal_ids:
        return {}

    result: dict[int, dict[str, Any]] = {}
    unique_ids = sorted(set(mal_ids))
    batches = [unique_ids[i:i + BATCH_SIZE] for i in range(0, len(unique_ids), BATCH_SIZE)]

    logger.info(
        "Fetching airing data from AniList for %d IDs in %d batches",
        len(unique_ids), len(batches),
    )

    for batch_num, batch_ids in enumerate(batches, 1):
        logger.info("AniList batch %d/%d (%d IDs)", batch_num, len(batches), len(batch_ids))

        page = 1
        while True:
            variables = {
                "idMal_in": batch_ids,
                "page": page,
                "perPage": BATCH_SIZE,
            }

            body = _request_with_rate_limit(variables)
            page_data = body.get("data", {}).get("Page", {})
            media_list = page_data.get("media", [])

            for media in media_list:
                mal_id = media.get("idMal")
                airing = media.get("nextAiringEpisode")
                if mal_id and airing:
                    result[mal_id] = airing

            has_next = page_data.get("pageInfo", {}).get("hasNextPage", False)
            if not has_next or not media_list:
                break

            page += 1

    logger.info("AniList: got airing data for %d anime", len(result))
    return result
