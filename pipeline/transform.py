"""Transform raw Jikan API responses into clean AnimeEntry objects."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from zoneinfo import ZoneInfo

from pipeline.schema import AnimeEntry


def _extract_genres(raw_genres: list[dict[str, Any]]) -> list[str]:
    """Extract genre names from Jikan genre objects."""
    return [g.get("name", "") for g in raw_genres if g.get("name")]


def _parse_broadcast_time(broadcast: Optional[dict[str, Any]]) -> str:
    """Extract the JST broadcast time from Jikan broadcast object.

    Returns 'Unknown' if no time is available.
    """
    if not broadcast:
        return "Unknown"
    time_str = broadcast.get("time")
    if not time_str:
        return "Unknown"
    return time_str


def _compute_next_air_utc(
    airing_day: str,
    airing_time: str,
    broadcast_timezone: str = "Asia/Tokyo",
) -> datetime:
    """Compute the next UTC air datetime from day and broadcast time.

    Converts from the broadcast timezone to UTC.
    Uses the current week to estimate the next airing date.
    Falls back to current UTC time if time cannot be parsed.
    """
    now = datetime.now(timezone.utc)

    day_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    target_weekday = day_map.get(airing_day.lower())
    if target_weekday is None or airing_time == "Unknown":
        return now

    try:
        hour, minute = map(int, airing_time.split(":"))
    except (ValueError, AttributeError):
        return now

    try:
        tz = ZoneInfo(broadcast_timezone)
    except (KeyError, ValueError):
        tz = ZoneInfo("Asia/Tokyo")

    now_local = now.astimezone(tz)
    current_weekday = now_local.weekday()
    days_ahead = target_weekday - current_weekday
    if days_ahead < 0:
        days_ahead += 7

    target_date = now_local.date() + timedelta(days=days_ahead)
    local_dt = datetime(
        target_date.year, target_date.month, target_date.day,
        hour, minute, 0, tzinfo=tz,
    )

    if local_dt <= now.astimezone(tz):
        local_dt += timedelta(days=7)

    return local_dt.astimezone(timezone.utc)


def _normalize_day(day_str: Optional[str]) -> str:
    """Normalize a day string to lowercase.

    Returns 'unknown' for None or empty strings.
    """
    if not day_str:
        return "unknown"
    normalized = day_str.strip().lower()
    valid_days = {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }
    if normalized not in valid_days:
        return "unknown"
    return normalized


def transform_anime(raw: dict[str, Any]) -> Optional[AnimeEntry]:
    """Transform a single raw Jikan anime object into an AnimeEntry.

    Returns None if the entry lacks required fields (id, title).
    """
    mal_id = raw.get("mal_id")
    title = raw.get("title")

    if not mal_id or not title:
        return None

    title_en = raw.get("title_english") or title

    images = raw.get("images", {})
    cover = images.get("jpg", {}).get("large_image_url", "")
    if not cover:
        cover = images.get("jpg", {}).get("image_url", "")

    genres = _extract_genres(raw.get("genres", []))
    score = raw.get("score")

    broadcast = raw.get("broadcast")
    airing_day_raw = broadcast.get("day", "") if broadcast else ""
    # Jikan returns day with trailing 's' like "Saturdays"
    airing_day = _normalize_day(
        airing_day_raw.rstrip("s") if airing_day_raw else None
    )

    airing_time = _parse_broadcast_time(broadcast)
    broadcast_timezone = (
        broadcast.get("timezone", "Asia/Tokyo") if broadcast else "Asia/Tokyo"
    )

    # Episode info
    aired_episodes = raw.get("episodes", 0) or 0
    airing_status = raw.get("status", "")
    if airing_status == "Currently Airing":
        next_episode = aired_episodes + 1
    else:
        next_episode = aired_episodes + 1

    total_episodes = raw.get("episodes")

    next_air_utc = _compute_next_air_utc(airing_day, airing_time, broadcast_timezone)

    mal_url = raw.get("url", f"https://myanimelist.net/anime/{mal_id}")

    return AnimeEntry(
        id=mal_id,
        title=title,
        title_en=title_en,
        cover=cover,
        genres=genres,
        score=score,
        airing_day=airing_day,
        airing_time=airing_time,
        broadcast_timezone=broadcast_timezone,
        next_episode=next_episode,
        total_episodes=total_episodes,
        next_air_utc=next_air_utc,
        mal_url=mal_url,
    )


def transform_schedule(raw_by_day: dict[str, list[dict[str, Any]]]) -> dict[str, list[AnimeEntry]]:
    """Transform a dict of day -> raw anime list into day -> AnimeEntry list.

    Entries that fail transformation are silently skipped.
    """
    week: dict[str, list[AnimeEntry]] = {}
    valid_days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    for day in valid_days:
        raw_list = raw_by_day.get(day, [])
        entries = []
        for raw in raw_list:
            entry = transform_anime(raw)
            if entry is not None:
                # Override airing_day to match the schedule day
                entry.airing_day = day
                entries.append(entry)
        week[day] = entries

    return week
