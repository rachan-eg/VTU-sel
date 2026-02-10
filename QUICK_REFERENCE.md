# Quick Reference Card

## Essential Commands

### Start System
```bash
docker compose up
```

### Rebuild After Changes
```bash
docker compose up --build
```

### Stop System
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f
```

### Restart
```bash
docker compose restart
```

---

## Configuration Quick Edit

### Required Settings
```env
# .env.docker
GEMINI_API_KEY=your_key
VTU_EMAIL=your_email@example.com
VTU_PASSWORD=your_password
```

### Show Browser (Debug)
```env
SELENIUM_HEADLESS=false
```

### Verbose Logging
```env
LOG_LEVEL=DEBUG
```

---

## Access Points

| Service | URL |
|---------|-----|
| Web UI | http://localhost:5000 |
| Logs | `docker compose logs` |
| Container Shell | `docker exec -it vtu-diary-bot bash` |

---

## Status Indicators

| Color | Status |
|-------|--------|
| 🔵 Blue | Running |
| 🟢 Green | Success |
| 🔴 Red | Error |

### Stages
1. **Processing with AI** - Formatting notes
2. **Browser Automation** - Logging in and submitting
3. **Complete** - Done!

---

## Common Issues & Fixes

| Issue | Quick Fix |
|-------|-----------|
| Can't connect | Wait 30s, check `docker ps` |
| Login fails | Check credentials in `.env.docker` |
| Form error | Delete `sessions/` folder |
| AI fails | Check API key validity |
| Port in use | Change `PORT=5001` in `.env.docker` |

---

## File Locations

| What | Where |
|------|-------|
| Config | `.env.docker` |
| Logs | `logs/app.log` |
| Sessions | `sessions/` |
| Error Screenshots | `screenshots/` |
| System Prompt | `system_prompts/diary_generator_system.txt` |

---

## Quick Debug

```bash
# View live logs
docker compose logs -f

# Check if running
docker ps

# Restart fresh
docker compose down
docker compose up --build

# Clear all data
rm -rf sessions/* logs/* screenshots/*
```

---

## Docker Management

```bash
# Stop and remove
docker compose down

# Remove volumes too
docker compose down -v

# Remove images
docker rmi vtu-sel-diary-automation

# Clean everything
docker system prune -a
```

---

## Environment Variables

| Variable | Values | Default |
|----------|--------|---------|
| LLM_PROVIDER | gemini, openai | gemini |
| SELENIUM_HEADLESS | true, false | true |
| PORT | 1024-65535 | 5000 |
| LOG_LEVEL | DEBUG, INFO, WARNING, ERROR | INFO |

---

## Testing

```bash
# Test without Docker
pip install -r requirements.txt
python app.py

# CLI mode
python main.py input/example.txt
```

---

## Update System

```bash
# Pull latest code
git pull

# Rebuild
docker compose down
docker compose up --build
```

---

## Backup Important Files

```bash
# Backup config
cp .env.docker .env.docker.backup

# Backup sessions (to avoid re-login)
tar -czf sessions_backup.tar.gz sessions/
```

---

## Performance Tips

- Keep `SELENIUM_HEADLESS=true` for speed
- Clear old sessions periodically: `rm sessions/*`
- Monitor logs size: `ls -lh logs/`
- Increase memory if Chrome crashes: Edit `shm_size` in `docker-compose.yml`

---

## Security Checklist

- [ ] `.env.docker` not committed to git
- [ ] Strong VTU password used
- [ ] API key kept private
- [ ] Regular password rotation
- [ ] Sessions cleared when sharing system

---

## Support

📘 [Full Documentation](DOCUMENTATION.md)
🏗️ [Architecture Diagram](ARCHITECTURE.txt)
🚀 [Setup Guide](SETUP.md)

**Need Help?**
1. Check logs: `docker compose logs`
2. Read troubleshooting in [DOCUMENTATION.md](DOCUMENTATION.md)
3. Create GitHub issue with logs

---

## Version Info

Check current version:
```bash
git log -1 --oneline
```

System info:
```bash
docker --version
docker compose --version
python --version
```
