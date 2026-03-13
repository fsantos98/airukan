/** A single anime entry with airing information. */
export interface AnimeEntry {
  id: number;
  title: string;
  title_en: string;
  cover: string;
  genres: string[];
  score: number | null;
  airing_day:
    | "monday"
    | "tuesday"
    | "wednesday"
    | "thursday"
    | "friday"
    | "saturday"
    | "sunday";
  airing_time: string;
  broadcast_timezone: string;
  next_episode: number;
  total_episodes: number | null;
  next_air_utc: string;
  mal_url: string;
}

/** Full weekly airing schedule. */
export interface Schedule {
  generated_at: string;
  week: {
    monday: AnimeEntry[];
    tuesday: AnimeEntry[];
    wednesday: AnimeEntry[];
    thursday: AnimeEntry[];
    friday: AnimeEntry[];
    saturday: AnimeEntry[];
    sunday: AnimeEntry[];
  };
}

/** Pipeline run metadata. */
export interface LastUpdated {
  utc: string;
  source: string;
}
