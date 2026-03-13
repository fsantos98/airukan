import CountdownTimer from "./CountdownTimer";
import type { AnimeEntry } from "../lib/types";
import { getAnimeLocalTime } from "../lib/timezone";

interface Props {
  anime: AnimeEntry;
  timezone: string;
}

export default function AnimeCardReact({ anime, timezone }: Props) {
  const localTime = getAnimeLocalTime(anime.next_air_utc, timezone);
  const episodeText = anime.total_episodes
    ? `Ep ${anime.next_episode} / ${anime.total_episodes}`
    : `Ep ${anime.next_episode}`;

  return (
    <article className="flex gap-4 rounded-xl bg-surface-light p-4 transition-colors hover:bg-surface-lighter">
      <img
        src={anime.cover || "/placeholder.svg"}
        alt={anime.title_en}
        className="h-36 w-24 rounded-lg object-cover"
        loading="lazy"
        width={96}
        height={144}
      />
      <div className="flex flex-1 flex-col justify-between">
        <div>
          <h3 className="font-semibold text-text leading-tight">
            <a
              href={anime.mal_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-primary-light transition-colors"
            >
              {anime.title_en}
            </a>
          </h3>
          {anime.title_en !== anime.title && (
            <p className="mt-0.5 text-xs text-text-muted">{anime.title}</p>
          )}
          <div className="mt-2 flex flex-wrap gap-1.5">
            {anime.genres.slice(0, 3).map((genre) => (
              <span
                key={genre}
                className="rounded-full bg-surface-lighter px-2 py-0.5 text-xs text-text-muted"
              >
                {genre}
              </span>
            ))}
          </div>
        </div>
        <div className="mt-3 flex items-end justify-between">
          <div className="text-sm">
            <span className="text-text-muted">{episodeText}</span>
            {anime.score !== null && (
              <span className="ml-2 text-primary-light">★ {anime.score}</span>
            )}
            <span className="ml-2 text-text-muted text-xs">{localTime}</span>
          </div>
          <CountdownTimer nextAirUtc={anime.next_air_utc} />
        </div>
      </div>
    </article>
  );
}
