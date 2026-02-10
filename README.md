# VTU Diary Automation

Raw notes → AI structures → Auto-submit

## Setup (2 minutes)

### 1. Configure

Edit `.env.docker`:

```env
GEMINI_API_KEY=your_actual_key
VTU_EMAIL=your_vtu_email@example.com
VTU_PASSWORD=your_password
```

### 2. Run

```bash
docker compose up
```

### 3. Use

Open: **http://localhost:5000**

Paste notes, hit submit, done.

## That's it

```
Your notes → AI → Browser → Done
```

## Documentation

📘 **[Complete Documentation](DOCUMENTATION.md)** - Architecture, components, troubleshooting
🔄 **[Browser Switching Guide](BROWSER_SWITCH.md)** - Toggle between Selenium and Playwright

## Key Features

- **Dual Browser Support**: Selenium (stable) or Playwright (modern) - switch via `BROWSER_ENGINE`
- **Smart Skill Selection**: AI chooses from 100+ VTU dropdown skills
- **Auto-reload**: Code changes restart server automatically
- **Session Persistence**: Login once, reuse for future runs

## Files

- `.env.docker` - Your credentials
- `app.py` - The automation (FastAPI)
- `templates/simple.html` - The UI
- `system_prompts/` - AI behavior config

## Run Locally (Alternative)

```bash
pip install -r requirements.txt
playwright install chromium  # If using Playwright
copy .env.docker .env
python app.py
```

Open: **http://localhost:5000**

## Troubleshooting

**Can't connect?**
- Wait 30s for browser to initialize
- Check: `docker compose logs` or terminal output

**Login failed?**
- Check VTU credentials in `.env` or `.env.docker`

**Form fields not filling?**
- Try switching: `BROWSER_ENGINE=playwright` (see [BROWSER_SWITCH.md](BROWSER_SWITCH.md))
- Check `screenshots/` folder for error captures

**Want to debug?**
- Run locally (not Docker) with `SELENIUM_HEADLESS=false` to see browser
