"""Pydantic models for the Airukan data pipeline."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class AnimeEntry(BaseModel):
    """A single anime entry with airing information."""

    id: int
    title: str
    title_en: str
    cover: str
    genres: list[str]
    score: Optional[float] = None
    airing_day: str
    airing_time_jst: str
    next_episode: int
    total_episodes: Optional[int] = None
    next_air_utc: datetime
    mal_url: str


class Schedule(BaseModel):
    """Full weekly airing schedule."""

    generated_at: datetime
    week: dict[str, list[AnimeEntry]]


class LastUpdated(BaseModel):
    """Metadata about the last pipeline run."""

    utc: datetime
    source: str = "jikan-v4"
