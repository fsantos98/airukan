"""Main entry point: fetches anime schedule data from Jikan API v4 and AniList."""

import logging
import time
from typing import Any

import requests

from pipeline.anilist import fetch_anilist_airing
from pipeline.transform import transform_schedule
from pipeline.writer import write_last_updated, write_raw_json, write_schedule

logger = logging.getLogger(__name__)

JIKAN_BASE_URL = "https://api.jikan.moe/v4"
REQUEST_DELAY = 1  # seconds between requests (Jikan rate limit: 3 req/sec)

DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def fetch_day_schedule(day: str) -> list[dict[str, Any]]:
    """Fetch the airing schedule for a single day from Jikan.

    Paginates through all pages to collect every entry.
    Respects rate limits with a delay between requests.
    """
    all_data: list[dict[str, Any]] = []
    page = 1

    while True:
        url = f"{JIKAN_BASE_URL}/schedules"
        params = {"filter": day, "page": page}

        logger.info("Fetching %s page %d", day, page)
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        body = response.json()
        data = body.get("data", [])
        all_data.extend(data)

        pagination = body.get("pagination", {})
        has_next = pagination.get("has_next_page", False)

        if not has_next or not data:
            break

        page += 1
        time.sleep(REQUEST_DELAY)

    return all_data


def fetch_all_schedules() -> dict[str, list[dict[str, Any]]]:
    """Fetch the full weekly schedule from Jikan, one day at a time.

    Returns a dict mapping day name to list of raw anime objects.
    """
    raw_by_day: dict[str, list[dict[str, Any]]] = {}

    for day in DAYS:
        raw_by_day[day] = fetch_day_schedule(day)
        time.sleep(REQUEST_DELAY)

    return raw_by_day


def main() -> None:
    """Run the full pipeline: fetch, transform, write."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    logger.info("Starting Airukan data pipeline")

    # Step 1: Fetch from Jikan
    logger.info("Fetching schedules from Jikan API...")
    raw_by_day = fetch_all_schedules()

    total = sum(len(v) for v in raw_by_day.values())
    logger.info("Fetched %d total anime entries across all days", total)

    # Save Jikan raw data
    jikan_path = write_raw_json(raw_by_day, "jikan_raw.json")
    logger.info("Saved Jikan raw data to %s", jikan_path)

    # Step 2: Fetch airing info from AniList
    logger.info("Fetching airing data from AniList...")
    all_mal_ids = [
        entry["mal_id"]
        for entries in raw_by_day.values()
        for entry in entries
        if entry.get("mal_id")
    ]
    anilist_data = fetch_anilist_airing(all_mal_ids)

    # Save AniList raw data
    anilist_path = write_raw_json(anilist_data, "anilist_raw.json")
    logger.info("Saved AniList raw data to %s", anilist_path)

    # Step 3: Transform (merge both sources)
    logger.info("Transforming data...")
    week = transform_schedule(raw_by_day, anilist_data=anilist_data)

    transformed_total = sum(len(v) for v in week.values())
    logger.info("Transformed %d entries", transformed_total)

    # Step 4: Write final output
    logger.info("Writing output files...")
    schedule_path = write_schedule(week)
    logger.info("Wrote %s", schedule_path)

    last_updated_path = write_last_updated()
    logger.info("Wrote %s", last_updated_path)

    logger.info("Pipeline complete!")


if __name__ == "__main__":
    main()
