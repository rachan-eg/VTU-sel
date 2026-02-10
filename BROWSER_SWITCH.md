# Switching Between Selenium and Playwright

Both browser automation engines are available. Switch between them using the `BROWSER_ENGINE` environment variable.

## Current Setup

**Selenium** (default) - Original implementation
**Playwright** (new) - Modern alternative with better reliability

## How to Switch

### Method 1: Environment Variable

Edit `.env.docker`:

```env
# Use Selenium (default)
BROWSER_ENGINE=selenium

# OR use Playwright
BROWSER_ENGINE=playwright
```

### Method 2: Docker Compose Override

```bash
docker compose run -e BROWSER_ENGINE=playwright diary-automation
```

## Differences

### Selenium
- ✅ Well-tested, currently working
- ✅ More online resources
- ❌ Requires manual waits and retries
- ❌ Complex selector logic

### Playwright
- ✅ Auto-waits for elements
- ✅ Better handling of modern web apps
- ✅ Simpler code
- ✅ Better debugging tools
- ⚠️ Needs testing with VTU portal

## Testing Playwright

1. **Edit `.env.docker`**:
   ```env
   BROWSER_ENGINE=playwright
   ```

2. **Rebuild and run**:
   ```bash
   docker compose up --build
   ```

3. **Test the automation** via http://localhost:5000

4. **Check logs**:
   ```bash
   docker logs vtu-diary-bot -f
   ```

5. **If it fails**, switch back to Selenium:
   ```env
   BROWSER_ENGINE=selenium
   ```
   ```bash
   docker compose restart
   ```

## File Structure

```
src/
├── core/              # Selenium implementation (original)
│   ├── driver.py
│   ├── auth.py
│   ├── navigation.py
│   └── form.py
│
├── playwright/        # Playwright implementation (new)
│   ├── driver.py
│   ├── auth.py
│   ├── navigation.py
│   ├── form.py
│   └── submitter.py
│
└── selenium_submit.py # Selenium facade
```

## Reverting to Selenium

If Playwright doesn't work, simply set `BROWSER_ENGINE=selenium` and restart. All Selenium code remains untouched.

## Debugging

**Playwright screenshots** are saved to `screenshots/` on error.

**View browser** (only works natively, not in Docker):
```env
SELENIUM_HEADLESS=false
```

**Check which engine is running**:
```bash
docker logs vtu-diary-bot | grep "Using"
# Output: "Using Playwright engine" or "Using Selenium engine"
```
