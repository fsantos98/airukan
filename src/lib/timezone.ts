import type { AnimeEntry } from "./types";

const STORAGE_KEY = "airukan_timezone";

export type DayName =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday";

export const WEEKDAYS: DayName[] = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

/** Read the user's timezone from localStorage, falling back to browser timezone. */
export function getUserTimezone(): string {
  if (typeof window === "undefined") return "UTC";
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return "UTC";
  }
}

/** Save the user's timezone preference to localStorage. */
export function setUserTimezone(tz: string): void {
  localStorage.setItem(STORAGE_KEY, tz);
}

/** Get the day of the week for an anime's next airing in the given timezone. */
export function getAnimeLocalDay(
  nextAirUtc: string,
  timezone: string,
): DayName {
  const date = new Date(nextAirUtc);
  const dayName = new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    timeZone: timezone,
  })
    .format(date)
    .toLowerCase() as DayName;
  return dayName;
}

/** Get the local time (HH:MM) for an anime's next airing in the given timezone. */
export function getAnimeLocalTime(
  nextAirUtc: string,
  timezone: string,
): string {
  const date = new Date(nextAirUtc);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: timezone,
  }).format(date);
}

/** Get today's day name in the given timezone. */
export function getTodayInTimezone(timezone: string): DayName {
  const now = new Date();
  const dayName = new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    timeZone: timezone,
  })
    .format(now)
    .toLowerCase() as DayName;
  return dayName;
}

/** Group anime entries by their airing day in the user's timezone, sorted by local time. */
export function groupAnimeByDay(
  allAnime: AnimeEntry[],
  timezone: string,
): Record<DayName, AnimeEntry[]> {
  const grouped: Record<DayName, AnimeEntry[]> = {
    monday: [],
    tuesday: [],
    wednesday: [],
    thursday: [],
    friday: [],
    saturday: [],
    sunday: [],
  };

  for (const anime of allAnime) {
    const day = getAnimeLocalDay(anime.next_air_utc, timezone);
    if (grouped[day]) {
      grouped[day].push(anime);
    }
  }

  for (const day of WEEKDAYS) {
    grouped[day].sort((a, b) => {
      const timeA = getAnimeLocalTime(a.next_air_utc, timezone);
      const timeB = getAnimeLocalTime(b.next_air_utc, timezone);
      return timeA.localeCompare(timeB);
    });
  }

  return grouped;
}
