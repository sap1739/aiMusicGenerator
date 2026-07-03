# Auralis

Auralis is an original, local-first AI music creation studio. It pairs a premium Next.js interface with a FastAPI job and library service, and integrates ACE-Step 1.5 through a narrow REST adapter. It does not use unofficial Suno APIs, cookies, scraping, or browser automation.

## What works

- Prompt + lyrics song jobs with artist-reference policy checks
- Authorized audio upload and metadata inspection
- Cover, repaint, vocal-to-BGM, style remix, and stem job flows
- Async in-process job runner with progress polling
- SQLite track library, versions, rename, delete, search, and provenance
- Audio streaming/download endpoint and generated demo WAVs
- Responsive creation studio, remix workspace, library, song detail, settings, and legal pages
- Demo mode that works without a GPU; ACE-Step REST mode is configuration-only

## Quick start

Requirements: Node 22+, Python 3.11–3.13, `uv`, and FFmpeg for production audio analysis/transcoding.

```bash
cp .env.example .env
npm install
cd apps/api && uv sync && uv run uvicorn auralis_api.main:app --reload --port 8000
```

In a second terminal:

```bash
npm run dev
```

Open `http://localhost:3000`; API docs are at `http://localhost:8000/docs`.

## ACE-Step 1.5

Run ACE-Step's official REST server separately, then set:

```env
AURALIS_ENGINE=ace_step
AURALIS_ACE_STEP_URL=http://localhost:8001
```

The adapter lives in `apps/api/src/auralis_api/engines/ace_step.py`. The API intentionally does not vendor model code or weights. Provider response shapes can evolve; the adapter isolates that surface.

## Commands

```bash
npm run lint
npm run typecheck
npm run build
npm test
npm run api:test
docker compose up --build
```

See [architecture](docs/ARCHITECTURE.md), [API reference](docs/API.md), [licensing](docs/THIRD_PARTY.md), and [phased plan](docs/IMPLEMENTATION_PLAN.md).
