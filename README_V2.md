# VTU Diary Automation v2.0 - Production Powerhouse 🚀

A completely redesigned, enterprise-grade automation system for VTU Internyet diary submissions with AI-powered bulk processing.

## 🌟 New Features

### Multi-Format Input Support
- **Text**: Plain text, Markdown
- **Audio**: MP3, WAV, M4A (transcribed via Whisper)
- **Video**: MP4, MOV (audio extraction + transcription)
- **Documents**: Excel, CSV, PDF
- **Unified Pipeline**: All formats normalized to consistent data structure

### Advanced Date Management
- **Ranges**: "2025-01-01 to 2025-01-31"
- **Relative**: "last week", "last month", "yesterday"
- **Lists**: ["2025-01-15", "2025-01-20", ...]
- **Smart Filtering**: Auto-skip weekends and holidays
- **Date Inference**: Extract dates from natural language

### Hyper-Intelligent AI Processing
- **Agentic Workflows**: LangChain-style agents with tools
- **Skill Matching**: Vector similarity search (FAISS) for 100+ VTU skills
- **Multi-Day Generation**: Batch API calls for efficiency
- **Confidence Scoring**: Flag low-confidence entries for review
- **Content Expansion**: Turn keywords into full 120-180 word entries

### Parallel & Scalable Automation
- **Multi-Context Browsers**: 5+ concurrent Playwright sessions
- **Async Processing**: ThreadPoolExecutor for AI generation
- **Rate Limiting**: Configurable delays between submissions
- **Retry Logic**: Exponential backoff for failed submissions

### Enhanced UI/UX
- **Web UI**: Modern bulk submission interface
- **WebSocket**: Real-time progress updates
- **CLI**: Powerful batch operations via Click
- **Progress Tracking**: Live status for 30+ day submissions

### Verification & Feedback
- **Screenshot Capture**: Pre/post submission evidence
- **Portal Scraping**: Verify successful submission
- **Database Tracking**: SQLite/PostgreSQL history
- **Detailed Logs**: Comprehensive error reporting

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         USER INTERFACE LAYER                 │
│  Web UI (FastAPI) | CLI (Click)             │
└─────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────┐
│       ORCHESTRATION LAYER                    │
│  Agentic Workflow Engine (AI Agent)         │
└─────────────────────────────────────────────┘
        │                │                │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ INPUT        │ │ AI           │ │ SUBMISSION   │
│ PIPELINE     │ │ PROCESSING   │ │ ENGINE       │
│ (Multi-      │ │ (Agent +     │ │ (Playwright  │
│  format)     │ │  LLM)        │ │  Parallel)   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Initialize database
python -m src.cli init
```

## 🚀 Usage

### Web UI (Recommended)
```bash
python app_new.py
# Navigate to http://localhost:5000
```

Upload file → Select date range → Click "Generate & Submit" → Watch progress in real-time!

### CLI (For Power Users)
```bash
# Bulk submit from Excel
python main_cli.py submit input/january.xlsx --dates "2025-01-01 to 2025-01-31"

# Dry run to preview
python main_cli.py submit input/notes.txt --dates "last week" --dry-run

# View history
python main_cli.py history --month 2025-01
```

## 🎯 Example Workflows

### Scenario 1: Backfill January from Sparse Excel
```bash
# Excel file with 5 keyword rows → 22 weekday entries
python main_cli.py submit input/jan_keywords.xlsx \
  --dates "2025-01-01 to 2025-01-31" \
  --workers 5

# Result: ~4 minutes for full month
```

### Scenario 2: Audio Notes → Diary Entries
```bash
# Record voice notes, transcribe, generate, submit
python main_cli.py submit input/weekly_notes.mp3 \
  --dates "last week"
```

### Scenario 3: PDF Report → Multiple Entries
```bash
# Extract text from PDF, distribute across dates
python main_cli.py submit input/internship_report.pdf \
  --dates "2025-01-15 to 2025-02-15"
```

## 🛠️ Configuration

Edit `.env` file:

```env
# LLM Provider
LLM_PROVIDER=openai  # or gemini
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-4-turbo-preview

# Browser
BROWSER_ENGINE=playwright  # or selenium
HEADLESS=true
MAX_PARALLEL_BROWSERS=5

# VTU Portal
PORTAL_LOGIN_URL=https://internyet.vtu.ac.in
VTU_USERNAME=your_username
VTU_PASSWORD=your_password

# Processing
BATCH_SIZE_DAYS=7  # Days per AI batch
CONFIDENCE_THRESHOLD=0.75
SKIP_WEEKENDS=true
SKIP_HOLIDAYS=true
```

## 📁 Project Structure

```
VTU-sel/
├── src/
│   ├── input/          # Multi-format processors
│   ├── ai/             # Agent, LLM client, skill DB
│   ├── automation/     # Parallel submission engine
│   ├── date_management/# Advanced date parsing
│   ├── api/            # FastAPI routes + WebSocket
│   ├── cli/            # Click commands
│   ├── db/             # SQLAlchemy models
│   └── utils/          # Logging, helpers
├── data/
│   ├── vtu_skills.json # 100+ VTU skills database
│   └── *.npy           # Cached embeddings
├── system_prompts/
│   └── multi_day_system.txt  # Enhanced AI prompt
├── templates/          # Web UI (HTML)
├── config.py           # Centralized config
├── app_new.py          # FastAPI app
└── main_cli.py         # CLI entry point
```

## 🎨 Key Differentiators

1. **10-20x Faster**: Parallel processing vs sequential
2. **Universal Input**: Text, Audio, Video, Excel, PDF
3. **Smart AI**: Agentic workflows with confidence scoring
4. **Production-Ready**: Retry logic, verification, DB tracking
5. **Scalable**: Handle 100+ days without breaking a sweat

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src tests/
```

## 📝 Examples

See `data/sample_inputs/` for:
- `example_january.xlsx` - Sparse keyword Excel
- `example_notes.txt` - Raw text notes
- `example_audio.mp3` - Voice memo

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Credits

Built with:
- FastAPI, Playwright, LangChain
- OpenAI Whisper, FAISS, Sentence Transformers
- Click, SQLAlchemy, Pydantic

---

**v2.0** - Turning months of manual work into minutes of automation ⚡
