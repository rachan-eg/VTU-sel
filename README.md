# VTU Internship Diary Automator

> **Production-ready automation for VTU students** - Transform messy notes into verified internship diary entries with AI assistance and safe portal submission.

[![Tests](https://img.shields.io/badge/tests-passing-success)](.)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](.)
[![License](https://img.shields.io/badge/license-MIT-green)](.)

---

## 🎯 Overview

A fully-fledged system that automates the transformation of raw daily notes into structured internship diary entries and safely submits them to the VTU Internyet portal. Built with **security, truth, and reliability** as core principles.

### Why This System?

- ✅ **Truth-Only AI**: Never fabricates facts - marks missing data explicitly
- ✅ **Git & Calendar Integration**: Automatically extract commits and events as proof
- ✅ **Human-in-the-Loop**: Preview, edit, and manually confirm before submission
- ✅ **Session Persistence**: Login once, reuse sessions for future submissions
- ✅ **Encrypted Audit Log**: Every action is recorded securely using AES encryption
- ✅ **Cost Tracking**: Monitor LLM API usage and estimated costs in real-time
- ✅ **Production-Ready**: Includes retry logic, error handling, tests, and CI/CD

---

## 🚀 Quickstart

### 1. Installation

```powershell
# Clone the repository
git clone <repo-url>
cd VTU-sel

# Install dependencies with UV (recommended - 10-100x faster)
uv sync

# Or with pip
pip install -r requirements.txt
```

### 2. Configuration

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env and configure:
# - LLM_PROVIDER (mock, gemini, or openai)
# - API keys (GEMINI_API_KEY or OPENAI_API_KEY)
# - AUDIT_SECRET_KEY (see below)
```

**Generate an encryption key for audit logs:**

```python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the output to your `.env` as `AUDIT_SECRET_KEY`.

### 3. Running the System

#### **Web UI (Recommended)**

```powershell
# Start the web server
python src/cli.py serve

# Open browser to: http://localhost:5000
```

#### **CLI Mode**

```powershell
# Generate diary from notes
python src/cli.py generate --input examples/today_notes.txt --output generated.json

# Submit to portal (dry-run)
python src/cli.py submit --entry generated.json --dry-run

# View audit log
python src/cli.py audit list
```

### 4. Run Tests

```powershell
pytest -v --cov=src
```

---

## 📁 Project Structure

```
VTU-sel/
├── src/
│   ├── cli.py                   # Professional CLI with full command suite
│   ├── llm_client.py            # LLM wrapper (Gemini/OpenAI/Mock) with retry & cost tracking
│   ├── diary_formatter.py       # Pydantic validation and word count checks
│   ├── selenium_submit.py       # Production-grade Selenium automation
│   ├── audit.py                 # Encrypted audit logging (AES)
│   ├── config.py                # Configuration management with validation
│   ├── integrations/
│   │   ├── git_client.py        # Git commit extraction
│   │   └── calendar_client.py   # Calendar event integration (stub)
│   ├── utils/
│   │   └── logger.py            # Centralized logging
│   └── web_preview/
│       ├── app.py               # Enhanced Flask application
│       └── templates/           # Premium web UI templates
├── system_prompts/
│   └── diary_generator_system.txt  # Truth-enforcing LLM system prompt
├── tests/
│   ├── test_llm_parsing.py      # Unit tests for diary formatting
│   ├── test_selenium.py         # Integration tests with HTML fixture
│   └── fixture.html             # Test HTML for Selenium
├── examples/
│   ├── today_notes.txt          # Sample raw notes
│   └── expected_output.json     # Expected LLM output
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions CI/CD
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project metadata
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🔐 Security & Privacy

### Truth-Only Rule
The LLM is constrained to produce entries **only from user-supplied inputs**. If facts are missing (e.g., meeting end time), they are marked as `null` and listed in the `uncertainties` array.

### No Auto-Submit
The Selenium automation will:
1. Fill the portal form
2. Highlight the "Save" button
3. **Wait for your manual click** in the browser

It will **never** click "Submit" without your explicit confirmation.

### Encrypted Audit
All raw inputs, LLM outputs, and portal responses are stored in an AES-encrypted file (`audit_log.enc`). The encryption key must be stored securely (ideally in OS keyring or `.env`).

### Credentials
Never store plaintext credentials. Configure API keys and secrets in `.env` (git-ignored) or use environment variables.

---

## 🧪 Testing

### Run All Tests
```powershell
pytest
```

### Run Specific Test Suites
```powershell
pytest tests/test_llm_parsing.py      # Unit tests only
pytest tests/test_selenium.py         # Integration tests (Selenium)
```

### Check Code Quality
```powershell
flake8 src      # Check for issues
black src       # Auto-format code with black
```

---

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | AI provider (`mock`, `gemini`, `openai`) | `mock` |
| `GEMINI_API_KEY` | Google Gemini API key | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `AUDIT_SECRET_KEY` | AES encryption key for audit logs | Auto-generated | 
| `FLASK_SECRET_KEY` | Flask session secret | `dev-secret` |
| `SELENIUM_HEADLESS` | Run browser headless (`true`/`false`) | `false` |
| `PORTAL_LOGIN_URL` | VTU portal login page | `https://internyet.vtu.ac.in/login` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Example `.env`

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
AUDIT_SECRET_KEY=your_generated_fernet_key_here
FLASK_SECRET_KEY=random_secret_for_sessions
SELENIUM_HEADLESS=false
LOG_LEVEL=INFO
```

---

## 📊 Features

### 1. **AI Diary Generation**
- Powered by Gemini or OpenAI (or mock mode for testing)
- Strict JSON schema enforcement
- Automatic retry on failure (exponential backoff)
- Token usage and cost tracking

### 2. **Git & Calendar Integration**
- Extract today's commits from local git repo
- Parse calendar events (extensible for Google Calendar, Outlook, etc.)
- Artifacts are included in LLM context for better accuracy

### 3. **Web Preview UI**
- Modern, responsive interface
- Real-time word count validation
- Uncertainty warnings
- Edit-before-submit workflow
- Audit log dashboard

### 4. **Selenium Portal Automation**
- Robust selector fallbacks
- Session persistence (cookies)
- Retry logic with screenshot capture
- Anti-detection measures
- Dry-run mode for testing

### 5. **Audit & Compliance**
- Encrypted JSON logs
- Rotation and export commands
- Timeline view with statistics
- Full traceability

---


---

## 🎓 Usage Examples

### CLI Workflow

```powershell
# 1. Generate from raw notes
python src/cli.py generate \
  --input examples/today_notes.txt \
  --output generated.json \
  --with-git

# 2. Preview the output
type generated.json

# 3. Submit to portal (dry-run first)
python src/cli.py submit \
  --entry generated.json \
  --hours 8 \
  --dry-run

# 4. View audit history
python src/cli.py audit list
```

### Web UI Workflow

1. Navigate to `http://localhost:5000`
2. Click "Generate Diary"
3. Paste your raw notes
4. Optionally enable Git/Calendar integration
5. Click "Generate Entry"
6. Review in Preview page
7. Edit if needed
8. Click "Confirm & Submit to Portal"
9. Manually confirm in browser

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

All PRs must pass CI checks (tests + linting).

---

## 📝 License

MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- Built for VTU students to streamline internship documentation
- Inspired by the need for truth-preserving automation
- Powered by modern LLMs with human oversight

---

**Ready to automate your internship diary?** Start with `python src/cli.py serve` and visit `http://localhost:5000`! 🚀
