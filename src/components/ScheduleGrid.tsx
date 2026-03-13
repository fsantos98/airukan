import { useState, useEffect } from "react";
import AnimeCardReact from "./AnimeCardReact";
import type { AnimeEntry } from "../lib/types";
import {
  getUserTimezone,
  groupAnimeByDay,
  WEEKDAYS,
  type DayName,
} from "../lib/timezone";

interface Props {
  allAnime: AnimeEntry[];
}

export default function ScheduleGrid({ allAnime }: Props) {
  const [timezone, setTimezone] = useState("UTC");

  useEffect(() => {
    setTimezone(getUserTimezone());
  }, []);

  const grouped = groupAnimeByDay(allAnime, timezone);

  return (
    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {WEEKDAYS.map((day) => {
        const entries = grouped[day as DayName] ?? [];
        return (
          <section key={day}>
            <h2 className="mb-4 text-lg font-bold text-primary-light capitalize">
              {day.charAt(0).toUpperCase() + day.slice(1)}
              <span className="ml-2 text-sm font-normal text-text-muted">
                ({entries.length} anime)
              </span>
            </h2>
            {entries.length > 0 ? (
              <div className="flex flex-col gap-3">
                {entries.map((anime) => (
                  <AnimeCardReact
                    key={`${anime.id}-${anime.next_air_utc}`}
                    anime={anime}
                    timezone={timezone}
                  />
                ))}
              </div>
            ) : (
              <p className="rounded-lg bg-surface-light p-6 text-center text-text-muted">
                Nothing airing
              </p>
            )}
          </section>
        );
      })}
    </div>
  );
}
