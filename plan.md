# Airukan — Architecture & Build Plan
> Pass this document to Claude Opus 4.6 to build the first release.

---

## What is Airukan?

A **static website** that tells users when the next episode of an anime is releasing. It is fast, simple, and has no traditional backend — only a scheduled data pipeline that writes JSON files consumed by the frontend.

---

## Core Philosophy

- **Static-first**: The website is 100% static HTML/CSS/JS. No server needed to serve pages.
- **Data via JSON**: A background process fetches anime schedule data and writes structured JSON files.
- **No database**: All persistent state lives in versioned JSON files on disk (or object storage).
- **Production-level**: Clear folder structure, typed code, tests, and CI/CD from day one.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Frontend | Astro (static output) | Fast, file-based routing, zero JS by default |
| Styling | Tailwind CSS | Utility-first, no runtime cost |
| Data pipeline | Python 3.12 | Simple scripts, great for scheduled jobs |
| Anime data source | Jikan API v4 (jikan.moe) | Free, no key required, wraps MyAnimeList |
| JSON storage | Local `/data/*.json` (or S3/R2 bucket) | Flat files, no DB overhead |
| Scheduler | GitHub Actions cron (or cron job on any VPS) | Zero infra cost |
| Hosting | Cloudflare Pages / Netlify / GitHub Pages | Free static hosting |
| Testing (pipeline) | pytest | Standard Python testing |
| Testing (frontend) | Playwright (E2E) + Vitest (unit) | Covers both UI and logic |

---

## Folder Structure

```
airukan/
├── .github/
│   └── workflows/
│       ├── fetch-data.yml        # Cron: runs pipeline, commits JSON
│       └── deploy.yml            # On push to main: build + deploy site
│
├── pipeline/                     # Python data fetcher
│   ├── fetch.py                  # Main entry: calls Jikan, writes JSON
│   ├── transform.py              # Cleans/normalises raw API response
│   ├── schema.py                 # Pydantic models for type safety
│   ├── writer.py                 # Writes output JSON files
│   └── tests/
│       ├── test_transform.py
│       ├── test_schema.py
│       └── test_writer.py
│
├── data/                         # ← Pipeline writes here, frontend reads here
│   ├── schedule.json             # Current season airing schedule
│   ├── upcoming.json             # Next season upcoming anime
│   └── last_updated.json         # Timestamp + pipeline run metadata
│
├── src/                          # Astro frontend
│   ├── pages/
│   │   ├── index.astro           # Homepage: today's schedule
│   │   ├── schedule.astro        # Full weekly schedule
│   │   └── anime/[id].astro      # Individual anime page
│   ├── components/
│   │   ├── AnimeCard.astro       # Card with cover, title, next ep time
│   │   ├── CountdownTimer.tsx    # React island: live countdown
│   │   ├── DayColumn.astro       # Groups anime by weekday
│   │   └── Header.astro
│   ├── layouts/
│   │   └── Base.astro
│   └── lib/
│       ├── data.ts               # Loads JSON at build time
│       └── time.ts               # Timezone helpers
│
├── tests/
│   ├── e2e/
│   │   └── schedule.spec.ts      # Playwright: renders schedule, countdown visible
│   └── unit/
│       └── time.test.ts          # Vitest: timezone + countdown logic
│
├── astro.config.mjs
├── tailwind.config.mjs
├── package.json
├── requirements.txt              # Python pipeline deps
└── README.md
```

---

## Data Pipeline — How It Works

### Step 1: Fetch (`pipeline/fetch.py`)

Calls the **Jikan API v4** endpoints:

```
GET https://api.jikan.moe/v4/schedules?filter=monday   (repeat for each day)
GET https://api.jikan.moe/v4/seasons/upcoming
```

Rate limit: Jikan allows 3 req/sec and 60 req/min — add `time.sleep(0.4)` between calls.

### Step 2: Transform (`pipeline/transform.py`)

Normalise raw API data into a clean internal shape:

```json
{
  "id": 12345,
  "title": "Solo Leveling",
  "title_en": "Solo Leveling",
  "cover": "https://cdn.myanimelist.net/...",
  "genres": ["Action", "Fantasy"],
  "score": 8.7,
  "airing_day": "saturday",
  "airing_time_jst": "23:00",
  "next_episode": 8,
  "total_episodes": 12,
  "next_air_utc": "2025-03-01T14:00:00Z",
  "mal_url": "https://myanimelist.net/anime/12345"
}
```

### Step 3: Write (`pipeline/writer.py`)

Writes three JSON files into `/data/`:

- `schedule.json` — array of all currently airing anime, grouped by weekday
- `upcoming.json` — next season's anime list  
- `last_updated.json` — `{ "utc": "2025-03-01T14:05:00Z", "source": "jikan-v4" }`

### Step 4: Schedule

GitHub Actions cron runs the pipeline **every 6 hours**, commits updated JSON back to the repo, which triggers a new static build + deploy automatically.

```yaml
# .github/workflows/fetch-data.yml
on:
  schedule:
    - cron: '0 */6 * * *'   # every 6 hours
  workflow_dispatch:          # manual trigger
```

---

## Frontend — Key Pages & Components

### `index.astro` — Homepage

- Reads `data/schedule.json` at build time via `src/lib/data.ts`
- Shows today's airing anime as cards sorted by air time
- Each card shows: cover image, title, episode number, and a **live countdown**

### `CountdownTimer.tsx` — React Island (client:load)

The only JavaScript that runs in the browser. Takes `next_air_utc` as a prop and counts down in real time. This is the only interactive component.

```tsx
// Hydrates client-side only
<CountdownTimer client:load nextAirUtc={anime.next_air_utc} />
```

### `schedule.astro` — Full Weekly Schedule

- Shows all 7 days in columns
- Each column lists that day's anime sorted by air time
- Empty days show a "Nothing airing" placeholder

### `anime/[id].astro` — Individual Anime Page

- Title, cover, score, genres, synopsis
- Next episode countdown (prominent)
- Episode list with air dates

---

## JSON Schema (TypeScript types for frontend)

```typescript
// src/lib/types.ts

export interface AnimeEntry {
  id: number;
  title: string;
  title_en: string;
  cover: string;
  genres: string[];
  score: number | null;
  airing_day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  airing_time_jst: string;       // "HH:MM"
  next_episode: number;
  total_episodes: number | null;  // null = unknown
  next_air_utc: string;           // ISO 8601
  mal_url: string;
}

export interface Schedule {
  generated_at: string;           // ISO 8601
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
```

---

## Pydantic Schema (Python pipeline)

```python
# pipeline/schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnimeEntry(BaseModel):
    id: int
    title: str
    title_en: str
    cover: str
    genres: list[str]
    score: Optional[float]
    airing_day: str
    airing_time_jst: str
    next_episode: int
    total_episodes: Optional[int]
    next_air_utc: datetime
    mal_url: str

class Schedule(BaseModel):
    generated_at: datetime
    week: dict[str, list[AnimeEntry]]
```

---

## Tests

### Python Pipeline Tests (`pytest`)

| File | What it tests |
|---|---|
| `test_transform.py` | Raw Jikan response → clean AnimeEntry (happy path + missing fields) |
| `test_schema.py` | Pydantic validation rejects bad data, accepts good data |
| `test_writer.py` | JSON files are written correctly, `last_updated.json` has correct timestamp |

Run with: `pytest pipeline/tests/ -v`

### Frontend Unit Tests (`vitest`)

| File | What it tests |
|---|---|
| `time.test.ts` | `getCountdown()` returns correct days/hours/min/sec; handles past dates; handles null |

Run with: `npm run test`

### E2E Tests (`Playwright`)

| File | What it tests |
|---|---|
| `schedule.spec.ts` | Homepage loads, at least one anime card is visible, countdown element exists in DOM, schedule page shows 7 day columns |

Run with: `npx playwright test`

---

## GitHub Actions Workflows

### `fetch-data.yml` — Data Pipeline

```
Trigger: cron every 6h + manual
Steps:
  1. Checkout repo
  2. Set up Python 3.12
  3. pip install -r requirements.txt
  4. python pipeline/fetch.py
  5. Run pytest (fail fast)
  6. git commit data/*.json if changed
  7. git push
```

### `deploy.yml` — Frontend Deploy

```
Trigger: push to main
Steps:
  1. Checkout repo
  2. Set up Node 20
  3. npm ci
  4. npm run test (vitest)
  5. npx playwright install
  6. npm run build
  7. npx playwright test (against built output)
  8. Deploy to Cloudflare Pages (or Netlify)
```

---

## `requirements.txt`

```
requests==2.31.0
pydantic==2.6.0
pytest==8.1.0
pytest-mock==3.12.0
python-dateutil==2.9.0
```

---

## `package.json` scripts

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "test": "vitest run",
    "test:e2e": "playwright test",
    "test:all": "vitest run && playwright test"
  }
}
```

---

## First Release Scope (v1.0)

Build only what is listed below. Nothing else.

- [ ] `pipeline/fetch.py` — fetches current season schedule from Jikan
- [ ] `pipeline/transform.py` — normalises to internal schema
- [ ] `pipeline/writer.py` — writes `data/schedule.json` and `data/last_updated.json`
- [ ] All pipeline pytest tests passing
- [ ] `src/pages/index.astro` — today's anime cards
- [ ] `src/pages/schedule.astro` — full weekly view
- [ ] `src/components/AnimeCard.astro` — card component
- [ ] `src/components/CountdownTimer.tsx` — live countdown React island
- [ ] `src/lib/data.ts` — JSON loader
- [ ] `src/lib/time.ts` — timezone/countdown helpers
- [ ] Vitest unit tests for `time.ts`
- [ ] Playwright E2E: homepage + schedule page
- [ ] `.github/workflows/fetch-data.yml`
- [ ] `.github/workflows/deploy.yml`
- [ ] `README.md` with setup + run instructions

**Not in v1**: search, user accounts, notifications, individual anime pages, upcoming season page, dark/light toggle. Keep it simple.

---

## Instructions for Claude Opus 4.6

1. Build each layer in order: **pipeline first**, then **frontend**, then **tests**, then **CI**.
2. Do not add features not listed in the v1 scope.
3. All Python must pass `mypy` and `ruff` linting.
4. All TypeScript must pass `tsc --noEmit`.
5. Every function must have a docstring or JSDoc comment.
6. Commit messages should follow conventional commits: `feat:`, `fix:`, `test:`, `chore:`.
7. The site must get a Lighthouse performance score of 90+ (static pages, minimal JS helps).
8. The `CountdownTimer` is the **only** client-side JS component. Everything else is server-rendered at build time.