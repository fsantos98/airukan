# Airukan

A static website that tells you when the next episode of an anime is releasing. Fast, simple, no backend — just a scheduled data pipeline that writes JSON files consumed by a static frontend.

## Tech Stack

- **Frontend**: [Astro](https://astro.build/) (static output) + [Tailwind CSS](https://tailwindcss.com/) v4
- **Data Pipeline**: Python 3.12 + [Pydantic](https://docs.pydantic.dev/)
- **Data Source**: [Jikan API v4](https://jikan.moe/) (free MyAnimeList wrapper)
- **Countdown**: React island (only client-side JS)

## Project Structure

```
airukan/
├── pipeline/          # Python data fetcher
│   ├── fetch.py       # Main: calls Jikan, writes JSON
│   ├── transform.py   # Cleans/normalises API response
│   ├── schema.py      # Pydantic models
│   ├── writer.py      # Writes output JSON files
│   └── tests/         # pytest tests
├── data/              # Pipeline writes here, frontend reads here
│   ├── schedule.json  # Current season airing schedule
│   └── last_updated.json
├── src/               # Astro frontend
│   ├── pages/         # index.astro, schedule.astro
│   ├── components/    # AnimeCard, CountdownTimer, etc.
│   ├── layouts/       # Base layout
│   └── lib/           # TS helpers (data loader, time utils)
├── tests/
│   ├── unit/          # Vitest tests
│   └── e2e/           # Playwright tests
└── .github/workflows/ # CI/CD
```

## Setup

### Prerequisites

- **Node.js** 20+
- **Python** 3.12+

### Install

```bash
# Frontend dependencies
npm install

# Python pipeline dependencies
pip install -r requirements.txt
```

### Run the Data Pipeline

```bash
python -m pipeline.fetch
```

This fetches the current anime schedule from Jikan and writes JSON files to `data/`.

### Development Server

```bash
npm run dev
```

Opens a local dev server at `http://localhost:4321`.

### Build for Production

```bash
npm run build
npm run preview
```

## Testing

### Pipeline Tests (Python)

```bash
pytest pipeline/tests/ -v
```

### Frontend Unit Tests (Vitest)

```bash
npm run test
```

### E2E Tests (Playwright)

```bash
# Build first, then run E2E
npm run build
npx playwright install --with-deps chromium
npm run test:e2e
```

### All Tests

```bash
npm run test:all
```

## CI/CD

- **`fetch-data.yml`**: Runs every 6 hours — fetches data, runs pipeline tests, commits updated JSON.
- **`deploy.yml`**: On push to main — runs tests, builds, deploys to GitHub Pages.

## License

MIT
