# VTU Diary Automation v2.0 - Quick Start Guide 🚀

## Installation (5 minutes)

### 1. Install Python Dependencies
```bash
cd "c:\Users\rkark\Documents\proj\Vtu\VTU-sel"
pip install -r requirements.txt
```

### 2. Install Playwright Browsers
```bash
playwright install chromium
```

### 3. Set Up Configuration
Create `.env` file with your settings:
```env
# LLM Provider (choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR use Gemini
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=your-gemini-key

# Browser Settings
BROWSER_ENGINE=playwright
HEADLESS=true
MAX_PARALLEL_BROWSERS=5

# VTU Portal (optional - can login manually)
PORTAL_LOGIN_URL=https://internyet.vtu.ac.in
VTU_USERNAME=your_username
VTU_PASSWORD=your_password

# Processing
BATCH_SIZE_DAYS=7
CONFIDENCE_THRESHOLD=0.75
SKIP_WEEKENDS=true
SKIP_HOLIDAYS=true
```

### 4. Initialize Database
```bash
python main_cli.py init
```

---

## Usage Methods

### Method 1: Web UI (Easiest) 🌐

```bash
# Start the web server
python app_new.py
```

Then open your browser to: `http://localhost:5000`

**Steps:**
1. Click "Choose File" and select your input (Excel, PDF, text, audio, etc.)
2. Enter date range: e.g., `2025-01-01 to 2025-01-31`
3. Check/uncheck options (Skip Weekends, Skip Holidays, Dry Run)
4. Click "🔥 Generate & Submit"
5. Watch the magic happen in real-time!

---

### Method 2: Command Line (Most Powerful) ⚡

#### Example 1: Submit from Excel
```bash
python main_cli.py submit input/my_january_notes.xlsx \
  --dates "2025-01-01 to 2025-01-31"
```

#### Example 2: Audio Transcription
```bash
python main_cli.py submit recordings/weekly_standup.mp3 \
  --dates "last week"
```

#### Example 3: Dry Run (Preview)
```bash
python main_cli.py submit notes.txt \
  --dates "2025-01-15 to 2025-01-20" \
  --dry-run
```

#### Example 4: Custom Workers
```bash
python main_cli.py submit input.xlsx \
  --dates "last month" \
  --workers 10 \
  --confidence-threshold 0.8
```

#### View History
```bash
# See all submissions for January
python main_cli.py history --month 2025-01

# Filter by status
python main_cli.py history --status success
```

---

## Input File Formats

### Excel/CSV
Create a file with these columns (auto-detected):
```
Date         | Hours | Activities
-------------|-------|---------------------------
2025-01-15   | 7     | Python REST API development
2025-01-16   | 6.5   | Testing and bug fixes
2025-01-17   | 7.5   | Documentation and deployment
```

**OR** just keywords (AI will expand):
```
Activities
------------------
Bug fixes
API development
Testing
Docs
Deploy
```

### Text File
```
January 15-17: Worked on Flask REST API. Set up authentication, CRUD operations, and testing.
Fixed several bugs related to JWT tokens. Deployed to staging environment.
```

### Audio/Video
Record yourself talking about your work. The system will:
1. Transcribe using Whisper
2. Extract key activities
3. Generate professional entries
4. Submit to portal

### PDF
Upload your internship report PDF. The system extracts text and distributes across dates.

---

## Common Workflows

### Workflow 1: Monthly Backfill from Sparse Data
```bash
# You have minimal notes, want to fill 30 days
python main_cli.py submit sparse_notes.txt \
  --dates "2025-01-01 to 2025-01-31"

# AI will intelligently distribute and vary content
```

### Workflow 2: Weekly Updates from Audio
```bash
# Record 5-minute voice memo every Friday
python main_cli.py submit friday_recap.mp3 \
  --dates "this week"
```

### Workflow 3: Bulk Import from Excel
```bash
# Prepare Excel with one row per day
python main_cli.py submit internship_log.xlsx \
  --dates "2025-01-01 to 2025-02-28" \
  --workers 10
```

---

## Pro Tips 💡

### 1. Use Dry Run First
Always test with `--dry-run` to preview generated entries:
```bash
python main_cli.py submit input.xlsx --dates "..." --dry-run
```

### 2. Adjust Confidence Threshold
Lower threshold = more automation, less review:
```bash
--confidence-threshold 0.6  # More aggressive (less manual review)
--confidence-threshold 0.9  # More conservative (more manual review)
```

### 3. Parallel Workers for Speed
More workers = faster submission (but more browser resources):
```bash
--workers 10  # Very fast, needs more RAM
--workers 3   # Slower, lighter on resources
```

### 4. Date Range Shortcuts
```bash
--dates "yesterday"
--dates "last week"
--dates "last month"
--dates "this week"
--dates "2025-01-15"  # Single day
```

### 5. Skip Filters
```bash
--no-skip-weekends    # Include Saturdays/Sundays
--no-skip-holidays    # Include holidays
```

---

## Troubleshooting

### Issue: "LLM_PROVIDER not set"
**Solution:** Add to `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
```

### Issue: "Playwright not found"
**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Issue: "Too many entries to process"
**Solution:** Reduce date range or increase workers:
```bash
--workers 10
```

### Issue: "Low confidence entries"
**Solution:**
- Provide more detailed input text
- Lower confidence threshold: `--confidence-threshold 0.6`
- Review flagged entries manually

### Issue: "Portal login failed"
**Solution:**
- Check VTU_USERNAME and VTU_PASSWORD in `.env`
- Try manual login (system will prompt)

---

## Next Steps

1. **Test with Dry Run:**
   ```bash
   python main_cli.py submit test_data.xlsx --dates "last week" --dry-run
   ```

2. **Submit Small Batch:**
   ```bash
   python main_cli.py submit test_data.xlsx --dates "2025-01-15 to 2025-01-17"
   ```

3. **Scale Up:**
   ```bash
   python main_cli.py submit full_month.xlsx --dates "2025-01-01 to 2025-01-31"
   ```

4. **Monitor Progress:**
   - Web UI: Watch real-time progress bar
   - CLI: See live status updates

5. **Verify Results:**
   ```bash
   python main_cli.py history --month 2025-01
   ```

---

## Support

- **Documentation:** See `README_V2.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Issues:** Check logs in `logs/` directory

---

**You're all set! Start automating! 🚀**
