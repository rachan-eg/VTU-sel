# VTU Diary Automation - Backend

FastAPI backend for VTU Diary Automation.

## Structure

```
backend/
├── app.py              # Main FastAPI application
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── src/                    # Source code modules
│   ├── ai/                 # AI/LLM integration
│   ├── api/                # REST API routes & models
│   ├── automation/         # Browser automation (Playwright)
│   ├── input/              # File processing (CSV, audio, PDF)
│   ├── db/                 # Database models & session
│   └── utils/              # Utilities (logging, etc.)
├── system_prompts/         # AI prompt templates
├── data/                   # Runtime data storage
├── logs/                   # Application logs
├── sessions/               # Browser session data
└── tests/                  # Unit & integration tests
```

## Running

**From backend directory:**
```bash
cd backend
python app.py
```

**With Docker:**
```bash
# Run from project root
cd ..
docker-compose up --build
```

See [../docker-compose.yml](../docker-compose.yml) for the full Docker setup.

## API Endpoints

- `GET /` - Serve React SPA
- `GET /health` - Health check
- `POST /api/upload-file` - Upload file for processing
- `POST /api/upload-text` - Upload raw text
- `POST /api/generate-preview` - Generate diary entries
- `POST /api/approve-and-submit` - Submit entries to VTU portal
- `GET /api/progress/{id}` - Get submission progress
- `GET /api/history` - Get submission history
- `WS /ws/progress/{id}` - WebSocket for real-time progress

API docs available at `/docs` when running.

## Configuration

Configuration is loaded from:
1. `.env` file in project root
2. Environment variables
3. `config.py` defaults

See [../.env.example](../.env.example) for all configuration options.

## Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt
playwright install chromium

# Run with hot reload
python app.py
```

## Testing

```bash
pytest tests/
```
