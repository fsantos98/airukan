"""Write processed anime data to JSON files."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from pipeline.schema import AnimeEntry, LastUpdated, Schedule


def _default_data_dir() -> Path:
    """Return the default data directory (project_root/data/)."""
    return Path(__file__).resolve().parent.parent / "data"


def write_schedule(
    week: dict[str, list[AnimeEntry]],
    data_dir: Path | None = None,
) -> Path:
    """Write the weekly schedule to schedule.json.

    Creates the data directory if it doesn't exist.
    Returns the path to the written file.
    """
    data_dir = data_dir or _default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    schedule = Schedule(
        generated_at=datetime.now(timezone.utc),
        week={day: entries for day, entries in week.items()},
    )

    output_path = data_dir / "schedule.json"
    output_path.write_text(
        schedule.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return output_path


def write_last_updated(data_dir: Path | None = None) -> Path:
    """Write pipeline run metadata to last_updated.json.

    Returns the path to the written file.
    """
    data_dir = data_dir or _default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    metadata = LastUpdated(
        utc=datetime.now(timezone.utc),
        source="jikan-v4",
    )

    output_path = data_dir / "last_updated.json"
    output_path.write_text(
        metadata.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return output_path
