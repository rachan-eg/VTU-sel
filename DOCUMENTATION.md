# VTU Diary Automation - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [System Flow](#system-flow)
4. [Components](#components)
5. [Setup & Installation](#setup--installation)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [Technical Details](#technical-details)
9. [Troubleshooting](#troubleshooting)
10. [File Structure](#file-structure)

---

## Overview

### What It Does
VTU Diary Automation is a system that automates the process of submitting internship diary entries to the VTU Internyet portal. It takes raw, unstructured notes and converts them into properly formatted diary entries using AI, then automatically submits them to the portal.

### Key Features
- **AI-Powered Formatting**: Converts any raw text into structured diary entries
- **Smart Skill Selection**: AI chooses from 100+ VTU dropdown skills based on task description
- **Dual Browser Support**: Selenium (stable) or Playwright (modern) - switch via `BROWSER_ENGINE`
- **Browser Automation**: Automatically logs in and submits to VTU portal
- **Simple Web UI**: Single-page interface for easy interaction
- **Docker-Ready**: Runs in isolated container with all dependencies
- **Session Persistence**: Login once, reuse session for future submissions
- **Auto-reload**: Development server restarts on code changes
- **Headless Mode**: Runs without visible browser (configurable)

### Technology Stack
- **Backend**: Python 3.11, FastAPI with uvicorn
- **AI**: Google Gemini / OpenAI
- **Browser Automation**: Selenium + Playwright (dual support)
- **Validation**: Pydantic
- **Containerization**: Docker & Docker Compose

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                    (Browser - localhost:5000)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                           │
│                         (app.py)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /          - Serve UI                              │   │
│  │  /submit    - Accept diary content                  │   │
│  │  /status    - Return automation status              │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Pipeline                       │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   AI Client  │ → │  Validation  │ → │ Transform to │   │
│  │ (LLM/Gemini) │   │  (Pydantic)  │   │  Form Data   │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Browser Automation Layer                    │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   Login to   │ → │  Navigate to │ → │  Fill & Submit│  │
│  │  VTU Portal  │   │  Diary Page  │   │     Form      │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Raw Text Input
    ↓
AI Processing (Gemini/OpenAI)
    ↓
Structured JSON (DiaryEntry model)
    ↓
Validation (Pydantic)
    ↓
Transform to Form Data
    ↓
Selenium Automation
    ↓
VTU Portal Submission
    ↓
Success/Error Status
```

---

## System Flow

### 1. User Submission
1. User opens web UI at `http://localhost:5000`
2. User pastes raw diary notes into textarea
3. User clicks "Submit" button
4. Frontend sends POST request to `/submit` endpoint

### 2. AI Processing
1. FastAPI server receives raw content
2. Starts async background task for processing
3. Loads system prompt from `system_prompts/diary_generator_system.txt`
4. Sends content to LLM (Gemini/OpenAI) for structuring
5. LLM returns structured JSON with:
   - Date
   - Entry text (120-180 words)
   - Activities list
   - Declaration
   - Confidence score
   - Uncertainties

### 3. Validation & Transformation
1. JSON validated against `DiaryEntry` Pydantic model
2. Transform to form data structure:
   - `description` ← entry_text
   - `hours` ← calculated from activities
   - `learnings` ← extracted from activities
   - `blockers` ← extracted from uncertainties
   - `links` ← extracted from artifacts
   - `skill_ids` ← default value

### 4. Browser Automation
1. Initialize Chrome with Selenium
2. Load saved session (if exists)
3. Navigate to VTU portal login page
4. Attempt auto-login with credentials
5. Navigate to diary entry page
6. Handle date/internship selection
7. Fill form fields
8. Submit form
9. Save session for future use

### 5. Status Updates
1. Frontend polls `/status` endpoint every 1 second
2. Backend updates status object with:
   - `running`: boolean
   - `stage`: "ai" | "browser" | "done" | "error"
   - `message`: current status message
   - `success`: boolean
   - `error`: error message (if any)

---

## Components

### 1. Web UI (`templates/simple.html`)
**Purpose**: Single-page interface for user interaction

**Features**:
- Dark mode minimal design
- Single textarea for raw input
- Real-time status updates with spinner
- Color-coded status (blue=running, green=success, red=error)

**JavaScript Functions**:
- `submit()`: Handle form submission
- `pollStatus()`: Poll backend for status updates
- `getStageText()`: Map stage to display text
- `showError()`: Display error messages
- `resetForm()`: Re-enable form after completion

### 2. FastAPI Server (`app.py`)
**Purpose**: Web server and orchestration layer

**Endpoints**:
- `GET /`: Serve HTML UI
- `POST /submit`: Accept diary content, start automation
- `GET /status`: Return current automation status

**Functions**:
- `submit()`: Validate input and start background task
- `run_automation_task()`: Main automation orchestrator (async)
- `get_status()`: Return current status object

### 3. LLM Client (`src/llm_client.py`)
**Purpose**: Interface with AI providers

**Features**:
- Provider abstraction (Gemini/OpenAI/Mock)
- Retry logic with exponential backoff
- Cost tracking
- Token usage monitoring

**Methods**:
- `generate()`: Send prompt and get structured response
- `_parse_response()`: Extract JSON from response

### 4. Diary Formatter (`src/diary_formatter.py`)
**Purpose**: Data validation and structure

**Models**:
```python
class Activity:
    start: Optional[str]
    end: Optional[str]
    duration_minutes: Optional[int]
    short_description: str
    artifacts: List[str]
    tags: List[str]
    inferred: bool

class DiaryEntry:
    date: str
    entry_text: str  # 120-180 words
    activities: List[Activity]
    declaration: str
    confidence_score: int
    uncertainties: List[str]
```

**Functions**:
- `validate_and_format()`: Validate JSON against model
- `check_word_count()`: Ensure entry_text is 120-180 words

### 5. Selenium Automation (`src/selenium_submit.py`)
**Purpose**: Browser automation facade

**Class: VTUSubmitter**
```python
__init__(headless, profile_name, wait_for_user)
login_manually(portal_url)
fill_diary(data, dry_run)
close()
```

### 6. Core Modules

#### Auth (`src/core/auth.py`)
- `login()`: Attempt auto-login to portal
- `manual_login_prompt()`: Wait for manual login if auto fails

#### Driver (`src/core/driver.py`)
- `setup_driver()`: Initialize Chrome with proper options
- Configure headless mode, window size, user agent

#### Form (`src/core/form.py`)
- `fill_diary()`: Main form filling logic with retry
- `_fill_once()`: Single attempt to fill form
- Handle multiple selector fallbacks for each field

#### Navigation (`src/core/navigation.py`)
- `ensure_on_diary_page()`: Navigate to correct page
- `handle_selection_page()`: Handle internship/date selection

#### Session (`src/core/session.py`)
- `save_session()`: Persist cookies to disk
- `load_session()`: Load cookies from disk

### 7. Data Transformation (`main.py`)
**Purpose**: Convert AI output to form format

```python
def transform_to_form_data(entry_data: dict) -> dict:
    """
    Input: DiaryEntry JSON
    Output: Form data dict with:
      - date
      - description
      - hours
      - learnings
      - blockers
      - links
      - skill_ids
    """
```

---

## Setup & Installation

### Prerequisites
- Docker & Docker Compose installed
- LLM API key (Gemini or OpenAI)
- VTU portal credentials

### Quick Setup

1. **Clone Repository**
```bash
git clone <repo-url>
cd VTU-sel
```

2. **Configure Environment**
```bash
# Edit .env.docker
GEMINI_API_KEY=your_key_here
VTU_EMAIL=your_email@example.com
VTU_PASSWORD=your_password
```

3. **Run**
```bash
docker compose up --build
```

4. **Access**
```
Open: http://localhost:5000
```

### Manual Setup (Without Docker)

1. **Install Python 3.11+**

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Chrome Browser**

4. **Configure Environment**
```bash
cp .env.docker .env
# Edit .env with your credentials
```

5. **Run**
```bash
python app.py
```

---

## Configuration

### Environment Variables

#### Required
```env
# LLM Provider
LLM_PROVIDER=gemini          # gemini or openai
GEMINI_API_KEY=your_key      # If using Gemini
# OPENAI_API_KEY=your_key    # If using OpenAI

# VTU Portal
VTU_EMAIL=your_email@example.com
VTU_PASSWORD=your_password
```

#### Optional
```env
# Portal URL (default shown)
PORTAL_LOGIN_URL=https://vtu.internyet.in/sign-in

# Browser Settings
BROWSER_ENGINE=selenium      # selenium or playwright (see BROWSER_SWITCH.md)
SELENIUM_HEADLESS=true       # true/false

# Web Server
PORT=5000
LOG_LEVEL=INFO              # DEBUG/INFO/WARNING/ERROR
```

### System Prompt Customization

Edit `system_prompts/diary_generator_system.txt` to customize how the AI structures your diary entries.

**Current Prompt Structure**:
1. Output format specification
2. Truth-only rule (no fabrication)
3. Word count requirement (120-180)
4. Field descriptions
5. Example output

---

## Usage

### Basic Workflow

1. **Prepare Your Notes**
   - Can be any format (bullet points, paragraphs, etc.)
   - Include date, activities, times (if known)
   - Mention commits, meetings, tasks

   Example:
   ```
   Today I worked on the authentication module.
   - Fixed bug where users couldn't login with special chars
   - Wrote unit tests
   - Pushed commit: fix login validation

   Had meeting at 2pm about security

   About 7 hours of work
   ```

2. **Submit via UI**
   - Open `http://localhost:5000`
   - Paste notes into textarea
   - Click "Submit"

3. **Monitor Progress**
   - Watch real-time status updates:
     - "Processing with AI..."
     - "Browser Automation..."
     - "Done! Diary submitted for [date]"

4. **Check Result**
   - Green success message = submission complete
   - Red error message = check logs

### CLI Usage (Alternative)

```bash
python main.py input/raw_input.txt
```

### Advanced Options

#### See Browser in Action
```env
SELENIUM_HEADLESS=false
```
Restart: `docker compose restart`

#### Change AI Provider
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

#### Dry Run (Test Without Submitting)
Modify `app.py` line 99:
```python
result = submitter.fill_diary(form_data, dry_run=True)
```

---

## Technical Details

### Docker Configuration

**Image**: Python 3.11 slim
**Chrome Installation**: Via official Google repository
**Shared Memory**: 2GB (required for Chrome)
**Volumes**:
- `./sessions` - Persistent login sessions
- `./logs` - Application logs
- `./system_prompts` - AI prompts

### Browser Configuration

**User Agent**: Standard Chrome on Linux
**Window Size**: 1920x1080
**Options**:
- `--no-sandbox`
- `--disable-dev-shm-usage`
- `--disable-gpu` (in headless)
- `--disable-blink-features=AutomationControlled`

### Browser Engine Selection

The system supports **two browser automation engines**:

#### Selenium (Default)
- ✅ Stable, well-tested
- ✅ Extensive online resources
- ⚠️ Requires manual waits
- ⚠️ Complex selector logic
- **Location**: `src/core/`

#### Playwright (Alternative)
- ✅ Auto-waits for elements
- ✅ Better modern web app support
- ✅ Simpler, more reliable
- ✅ Better debugging (screenshots, traces)
- **Location**: `src/playwright/`

**Switching**: Set `BROWSER_ENGINE=playwright` or `selenium` in `.env`

See **[BROWSER_SWITCH.md](BROWSER_SWITCH.md)** for complete switching guide.

### AI Skill Selection

The AI intelligently selects **1-3 skills** from VTU's predefined dropdown (100+ options):

**Examples**:
- "Fixed React component bugs" → `["React", "JavaScript", "HTML"]`
- "Trained ML model" → `["Python", "Machine learning", "TensorFlow"]`
- "Deployed with Docker" → `["Docker", "DevOps", "Kubernetes"]`

Skills list configured in `system_prompts/diary_generator_system.txt`

### Form Filling Strategy

**Multiple Selector Fallbacks**:
Each form field has 3-5 fallback selectors:
```python
[
    (By.NAME, "description"),
    (By.ID, "description"),
    (By.XPATH, "//textarea[contains(@placeholder, 'Description')]"),
    (By.CSS_SELECTOR, "textarea[name='description']")
]
```

**Retry Logic**: Up to 3 attempts with 2s delay

**Event Triggering**: Dispatch input/change/blur events for React forms

### Session Management

**Storage**: `sessions/[profile_name]_cookies.pkl`
**Format**: Pickled list of cookies
**Expiry**: Handled by server (usually 24 hours)

### Error Handling

**Levels**:
1. Try all selector variants
2. Retry entire form fill (3x)
3. Capture screenshot on failure
4. Return error to user

**Screenshots**: Saved to `screenshots/error_attempt_[N].png`

---

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails
**Symptom**: Error during `docker compose up`
**Solution**:
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker compose build --no-cache
docker compose up
```

#### 2. Chrome Won't Start
**Symptom**: "Chrome binary not found"
**Solution**:
- Verify Chrome installed in Docker image
- Check `docker compose logs` for details
- Increase `shm_size` if memory error

#### 3. Login Fails
**Symptom**: "Login failed" or stuck at login page
**Solutions**:
- Verify VTU credentials in `.env.docker`
- Check portal URL is correct
- Try with `SELENIUM_HEADLESS=false` to see what's happening
- Delete `sessions/` folder to clear old session

#### 4. Form Submission Fails
**Symptom**: "Could not find field" errors
**Solutions**:
- Portal HTML might have changed
- Check `screenshots/` for debug images
- Update selectors in `src/core/form.py`

#### 5. AI Generation Fails
**Symptom**: "Failed to parse response" or "API error"
**Solutions**:
- Verify API key is valid
- Check API quota/billing
- Try different provider (Gemini ↔ OpenAI)
- Check `logs/` for detailed error

#### 6. Can't Connect to UI
**Symptom**: `localhost:5000` not loading
**Solutions**:
```bash
# Check container running
docker ps

# Check logs
docker compose logs

# Verify port not in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Mac/Linux
```

### Debug Mode

**Enable Verbose Logging**:
```env
LOG_LEVEL=DEBUG
```

**View Live Logs**:
```bash
docker compose logs -f
```

**Inspect Container**:
```bash
docker exec -it vtu-diary-bot bash
```

---

## File Structure

```
VTU-sel/
├── app.py                          # FastAPI web server
├── main.py                         # CLI entry point & transformations
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Service orchestration
├── requirements.txt                # Python dependencies
├── .env.docker                     # Environment config (edit this!)
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git exclusions
│
├── README.md                       # Quick start guide
├── SETUP.md                        # 3-step setup
├── DOCUMENTATION.md                # This file
│
├── templates/
│   └── simple.html                 # Web UI
│
├── src/
│   ├── llm_client.py              # LLM interface
│   ├── diary_formatter.py         # Pydantic models
│   ├── selenium_submit.py         # Automation facade
│   ├── config.py                  # Config management
│   ├── audit.py                   # Audit logging (unused)
│   ├── commands.py                # CLI commands (unused)
│   │
│   ├── core/
│   │   ├── auth.py                # Login logic
│   │   ├── driver.py              # Browser setup
│   │   ├── form.py                # Form filling
│   │   ├── navigation.py          # Page navigation
│   │   ├── session.py             # Cookie management
│   │   ├── utils.py               # Helper functions
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── llm/                   # LLM implementations
│   │       ├── base.py
│   │       ├── gemini.py
│   │       ├── openai.py
│   │       └── mock.py
│   │
│   ├── utils/
│   │   └── logger.py              # Logging setup
│   │
│   ├── integrations/              # Optional integrations
│   │   ├── git_client.py
│   │   └── calendar_client.py
│   │
│   └── web_preview/               # Old web UI (unused)
│
├── system_prompts/
│   └── diary_generator_system.txt  # AI system prompt
│
├── examples/
│   ├── today_notes.txt            # Example input
│   └── expected_output.json       # Example output
│
├── input/
│   ├── .gitkeep
│   └── example.txt                # Sample diary notes
│
├── sessions/                      # Saved login sessions
│   └── .gitkeep
│
├── logs/                          # Application logs
│   └── .gitkeep
│
└── screenshots/                   # Error screenshots
    └── .gitkeep
```

### Key Files Explained

**Configuration**:
- `.env.docker` - **EDIT THIS** with your credentials

**Entry Points**:
- `app.py` - Web UI mode (recommended)
- `main.py` - CLI mode (alternative)

**Core Logic**:
- `src/llm_client.py` - AI communication
- `src/core/form.py` - Form automation
- `src/core/auth.py` - Login handling

**User Interface**:
- `templates/simple.html` - Single-page UI

**Persistence**:
- `sessions/` - Login cookies
- `logs/` - Debug logs
- `screenshots/` - Error captures

---

## API Reference

### POST /submit
Submit diary content for processing

**Request**:
```json
{
  "content": "Raw diary notes..."
}
```

**Response**:
```json
{
  "status": "started"
}
```

### GET /status
Get current automation status

**Response**:
```json
{
  "running": true,
  "stage": "browser",
  "message": "Filling form...",
  "success": false,
  "error": null
}
```

**Stages**:
- `ai` - Processing with AI
- `browser` - Browser automation
- `done` - Complete
- `error` - Failed

---

## Security Notes

### Credentials Storage
- Environment variables (`.env.docker`)
- **Never commit** `.env.docker` to git
- Add to `.gitignore`

### Session Cookies
- Stored in `sessions/` directory
- Encrypted by browser
- Auto-expire after 24 hours (server-controlled)

### API Keys
- Stored in environment only
- Not logged
- Transmitted over HTTPS to API providers

### Recommendations
1. Use strong VTU password
2. Rotate API keys regularly
3. Don't share Docker containers with credentials
4. Use read-only API keys where possible

---

## Performance

**Typical Execution Times**:
- AI Processing: 3-10 seconds
- Browser Login: 2-5 seconds
- Form Fill: 2-4 seconds
- **Total**: 10-20 seconds per submission

**Resource Usage**:
- Memory: ~500MB (Chrome) + 100MB (Python)
- CPU: Minimal (mostly I/O bound)
- Disk: ~1GB (Docker image)

---

## Extending the System

### Add New AI Provider

1. Create `src/core/llm/newprovider.py`
2. Inherit from `BaseLLMClient`
3. Implement `generate()` method
4. Register in `src/llm_client.py`

### Customize AI Output

Edit `system_prompts/diary_generator_system.txt` to:
- Change word count requirements
- Add new fields
- Modify formatting rules
- Add validation rules

### Add Email Notifications

Uncomment email code in `app.py` and configure SMTP settings.

### Add More Form Fields

1. Update transform in `main.py`
2. Add selectors in `src/core/form.py`
3. Test with dry_run=True

---

## Support

**Issues**: Create issue on GitHub
**Logs**: Check `docker compose logs`
**Debug**: Set `LOG_LEVEL=DEBUG`

---

## License

MIT License - See LICENSE file

---

## Credits

Built for VTU students to automate internship diary submissions.
Powered by AI (Gemini/OpenAI) with human oversight.

---

**Last Updated**: 2026-02-10
**Version**: 1.0.0
