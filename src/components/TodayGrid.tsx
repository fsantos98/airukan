import { useState, useEffect } from "react";
import AnimeCardReact from "./AnimeCardReact";
import type { AnimeEntry } from "../lib/types";
import {
  getUserTimezone,
  getTodayInTimezone,
  getAnimeLocalDay,
  getAnimeLocalTime,
} from "../lib/timezone";

interface Props {
  allAnime: AnimeEntry[];
}

export default function TodayGrid({ allAnime }: Props) {
  const [timezone, setTimezone] = useState("UTC");

  useEffect(() => {
    setTimezone(getUserTimezone());
  }, []);

  const todayKey = getTodayInTimezone(timezone);
  const todayLabel = todayKey.charAt(0).toUpperCase() + todayKey.slice(1);

  const todayAnime = allAnime.filter(
    (anime) => getAnimeLocalDay(anime.next_air_utc, timezone) === todayKey,
  );

  const sorted = [...todayAnime].sort((a, b) => {
    const timeA = getAnimeLocalTime(a.next_air_utc, timezone);
    const timeB = getAnimeLocalTime(b.next_air_utc, timezone);
    return timeA.localeCompare(timeB);
  });

  return (
    <div>
      <p className="mb-8 text-text-muted">
        {todayLabel} — {sorted.length} anime airing
      </p>

      {sorted.length > 0 ? (
        <div className="flex flex-col gap-4">
          {sorted.map((anime) => (
            <AnimeCardReact
              key={`${anime.id}-${anime.next_air_utc}`}
              anime={anime}
              timezone={timezone}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-xl bg-surface-light p-12 text-center">
          <p className="text-xl text-text-muted">No anime airing today</p>
          <p className="mt-2 text-sm text-text-muted">
            Check the{" "}
            <a
              href="/airukan/schedule"
              className="text-primary-light hover:underline"
            >
              full schedule
            </a>{" "}
            for other days.
          </p>
        </div>
      )}
    </div>
  );
}
