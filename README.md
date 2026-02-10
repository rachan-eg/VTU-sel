# VTU Diary Automation v3.0 — GOD MODE

Automated internship diary generation and submission for VTU's Internyet portal.

Feed it anything — voice memos, Excel logs, git histories, photos of whiteboards. It generates months of perfectly plausible, evaluator-satisfying diary entries in seconds.

## Features

- **Universal input ingestion** — CSV, Excel, text, audio, PDF, images
- **AI diary generation** — Gemini/Groq/Cerebras/OpenAI with auto-fallback
- **Single-call optimization** — All entries in one LLM call, no quota waste
- **Date-mapped processing** — Each date gets only its own tasks, no mixing
- **Playwright automation** — Sequential submission with exact recorded selectors
- **Modern React UI** — Tailwind + shadcn/ui-inspired frontend
- **Plausibility scoring** — Warns when entries get too convincing
- **Self-healing selectors** — Auto-detects VTU portal changes

## Quick Start

### 1. Install Dependencies

```bash
# Python deps
pip install -r requirements.txt

# Playwright browser
playwright install chromium

# Frontend (optional)
cd frontend
npm install
npm run build  # outputs to ../static/
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
# Required
VTU_EMAIL=your_vtu_email@example.com
VTU_PASSWORD=your_vtu_password

# At least one LLM API key
GROQ_API_KEY=gsk_xxxxx              # Free tier: 14,400 req/day
# GEMINI_API_KEY=AIza_xxxxx         # Free tier: 20 req/day
# CEREBRAS_API_KEY=csk_xxxxx        # Paid
# OPENAI_API_KEY=sk-xxxxx           # Paid
```

### 3. Run

```bash
python app_new.py
# Open http://localhost:5000
```

For development with hot reload:
```bash
# Terminal 1: Frontend dev server
cd frontend && npm run dev   # :3000

# Terminal 2: Backend API
python app_new.py            # :5000
```

## Usage

### Web UI Flow

1. **Upload** — Drop any file or paste text
2. **Date Range** — Select from/to dates, skip weekends/holidays
3. **Generate** — AI creates entries in seconds
4. **Preview** — Review, edit, check plausibility scores
5. **Launch** — Playwright swarm submits to VTU portal
6. **History** — View all submissions, export CSV

### Supported Input Formats

| Format | Example | Processor |
|--------|---------|-----------|
| Excel/CSV | Task logs with Date/Task/Duration columns | Auto-detects headers |
| Text | Meeting notes, bullet points | Pass-through |
| Audio | Voice memos (.mp3, .wav, .m4a) | Whisper STT |
| PDF | Reports, documents | pdfplumber |
| Images | Whiteboard photos | OCR (future) |

### CSV Structure (Auto-Detected)

The system auto-detects CSV headers. Your CSV can have:
- `Date` / `Day` / `When` → mapped to entry dates
- `Task` / `Activity` / `Work` / `Description` → main content
- `Hours` / `Duration` / `Task Duration` → hours worked
- `Skills` → pre-selected skills

Example:
```csv
Date,Application,Task,Task Duration,Status
05-01-2026,PitchSync,Onboarding and setup,8,Completed
06-01-2026,PitchSync,Research cloud features and design workshop,8,Completed
```

## Architecture

### AI Pipeline

```
Input (any format)
  ↓
Excel/Text/Audio Processor → Raw text per row
  ↓
Date Mapper → Associate each row with its date
  ↓
Single LLM Call → Generate all entries at once
  ↓
Plausibility Engine → Score each entry
  ↓
Preview UI → User reviews/edits
  ↓
Playwright Engine → Submit to VTU portal
```

### LLM Provider Chain

Set `LLM_PROVIDER=auto` in `.env` to enable automatic fallback:

```
groq (14,400/day free) → gemini (20/day free) → cerebras (paid) → openai (paid)
```

On quota exhaustion or 402/429 errors, instantly fails over to next provider.

### Submission Engine

**Playwright** (default):
- Sequential mode — one page, all entries
- Login once, reuse session for all entries
- Native `get_by_role` selectors from codegen recording
- React state updates via `dispatch_event`
- Force-enable disabled Save button via JS

**Selenium** (fallback):
- Available if Playwright unavailable
- Slower, more resource-intensive

## Configuration

### Environment Variables

See [`.env.example`](.env.example) for all options.

Key settings:

```bash
# LLM
LLM_PROVIDER=auto                # auto, groq, gemini, cerebras, openai
BATCH_SIZE_DAYS=20               # Days per API call (higher = fewer calls)

# Browser
HEADLESS=true                    # Run browsers headless
MAX_PARALLEL_BROWSERS=2          # Concurrent workers (Playwright sequential, this is ignored)

# Portal
PORTAL_LOGIN_URL=https://vtu.internyet.in/sign-in
```

### System Prompt

Located at [`system_prompts/god_mode_system.txt`](system_prompts/god_mode_system.txt).

Key directives:
- 150-200 words per entry (rich, detailed)
- Write like a real engineering student, not AI
- Pick skills ONLY from actual work (no random Ruby on Rails)
- Strict date isolation — no mixing tasks across dates
- Hours always 8

## Troubleshooting

**"No module named 'playwright'"**
```bash
pip install playwright
playwright install chromium
```

**"All providers exhausted"**
- Add at least one valid API key to `.env`
- Check your quota/billing for each provider

**"Field not found: Description"**
- The recorded selectors might be stale
- Re-run `playwright codegen` and update selectors in `submission_engine.py`

**Database issues**
```bash
rm vtu_automation.db    # Delete and restart to recreate
```

**Session issues**
```bash
rm -rf sessions/ auth_state.json
```

## File Structure

```
VTU-sel/
├── app_new.py                    # FastAPI backend + SPA server
├── config.py                     # Centralized configuration
├── frontend/                     # React + Vite + Tailwind UI
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/                # Dashboard, Upload, Preview, Progress, History
│   │   ├── components/           # PlausibilityGauge, EntryCard, FileDropzone, etc.
│   │   └── lib/                  # API client, utils
│   ├── package.json
│   └── vite.config.ts
├── src/
│   ├── ai/
│   │   ├── agent.py              # Single-call diary generation with date mapping
│   │   ├── llm_client.py         # Multi-provider fallback chain
│   │   └── vtu_skills.py         # Curated skills list
│   ├── automation/
│   │   └── submission_engine.py  # Playwright sequential submission
│   ├── input/
│   │   ├── excel_processor.py    # Auto-header detection, any CSV schema
│   │   ├── audio_processor.py    # Whisper STT
│   │   └── router.py             # Multi-format routing
│   ├── core/
│   │   ├── form.py               # Selenium form fill (legacy)
│   │   └── navigation.py         # Selenium navigation (legacy)
│   ├── plausibility/
│   │   └── engine.py             # Multi-axis entry scoring
│   ├── self_healing/
│   │   └── selectors.py          # Auto-recovering selectors + stealth
│   ├── api/
│   │   ├── routes.py             # FastAPI endpoints
│   │   └── models.py             # Pydantic schemas
│   └── db/
│       ├── models.py             # SQLAlchemy ORM
│       └── session.py            # DB connection
├── system_prompts/
│   └── god_mode_system.txt       # The main prompt
└── static/                       # Built React app (from frontend/build)
```

## Development

### Recording Portal Selectors

When VTU updates their portal:

```bash
playwright codegen https://vtu.internyet.in/sign-in -o recorded_flow.py
```

Walk through: login → diary page → select internship → pick date → fill form → save.

Update `src/automation/submission_engine.py` with the new selectors.

### Adding LLM Providers

1. Create `src/core/llm/your_provider.py` implementing `LLMProvider` interface
2. Add to `src/ai/llm_client.py` registry
3. Add `YOUR_PROVIDER_API_KEY` to `config.py`

### Modifying Skills List

Edit `src/ai/vtu_skills.py` — add/remove from the `VTU_SKILLS` array.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload-file` | POST | Upload file, get upload_id |
| `/api/upload-text` | POST | Upload raw text, get upload_id |
| `/api/generate-preview` | POST | Generate entries for preview |
| `/api/approve-and-submit` | POST | Submit approved entries (background) |
| `/api/progress/{id}` | GET | Get submission progress |
| `/api/history` | GET | Get submission history |
| `/api/history/stats` | GET | Get stats (total, success rate) |
| `/ws/progress/{id}` | WS | WebSocket progress stream |

## Tech Stack

**Backend:**
- FastAPI + Uvicorn
- Playwright (async browser automation)
- SQLAlchemy (SQLite)
- Pydantic (validation)
- Whisper (audio transcription)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Framer Motion (animations)
- Recharts (visualizations)

**AI:**
- Groq, Gemini, Cerebras, OpenAI (multi-provider)
- Automatic fallback chain
- Single-call optimization

## License

MIT

## Warning

This tool automates form submission. Use responsibly and in accordance with your institution's policies.
