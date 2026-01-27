import json
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from llm_client import LLMClient, LLMError
from diary_formatter import validate_and_format, check_word_count
from audit import append_audit
from selenium_submit import VTUSubmitter, SubmitError
from config import Config
from integrations.git_client import GitClient
from integrations.calendar_client import CalendarClient
from utils.logger import setup_logger

logger = setup_logger(__name__)
config = Config()
router = APIRouter() # Prefix can be added in app inclusion

@router.post("/api/generate")
async def api_generate(request: Request):
    try:
        data = await request.json()
        raw_text = data.get("raw_text")
        
        if not raw_text:
            return JSONResponse({"error": "No raw text provided"}, status_code=400)
        
        artifacts = {}
        if data.get("with_git"):
            try:
                commits = GitClient(".").get_today_commits()
                if commits: artifacts["commits"] = commits
            except Exception as e:
                logger.warning(f"Git failed: {e}")
        
        if data.get("with_calendar"):
            try:
                events = CalendarClient().get_today_events()
                if events: artifacts["events"] = events
            except Exception as e:
                logger.warning(f"Calendar failed: {e}")
        
        augmented_text = raw_text
        if artifacts:
            augmented_text += "\n\nADDITIONAL ARTIFACTS:\n" + json.dumps(artifacts, indent=2)
        
        client = LLMClient(provider=config.llm_provider)
        # Fix path: src/web_preview/routes/api.py -> src/../system_prompts
        root_dir = Path(__file__).parent.parent.parent.parent
        system_prompt = (root_dir / "system_prompts" / "diary_generator_system.txt").read_text()
        
        result = client.generate_diary(augmented_text, system_prompt)
        validate_and_format(result)
        word_check = check_word_count(result["entry_text"])
        
        request.session['last_entry'] = result
        request.session['raw_text'] = raw_text
        request.session['word_check'] = word_check
        request.session['usage_stats'] = client.get_usage_stats()
        
        append_audit({
            "event": "web_generate",
            "raw_text": raw_text,
            "llm_output": result,
            "status": "generated"
        })
        
        return {
            "success": True,
            "entry": result,
            "word_check": word_check,
            "usage_stats": client.get_usage_stats()
        }
        
    except LLMError as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    except Exception as e:
        logger.error(f"Gen error: {e}", exc_info=True)
        return JSONResponse({"error": f"Internal error: {e}"}, status_code=500)

@router.post("/save")
async def save(request: Request):
    try:
        data = await request.json()
        entry = request.session.get('last_entry', {})
        entry['final_text'] = data.get("text")
        
        append_audit({
            "event": "manual_save",
            "raw_text": request.session.get('raw_text'),
            "llm_output": entry,
            "status": "saved_locally"
        })
        return {"message": "✓ Saved locally"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post("/submit")
async def submit(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        date = data.get("date")
        entry = request.session.get('last_entry', {})
        
        data_to_fill = {
            "date": date or entry.get("date"),
            "description": text,
            "hours": entry.get("total_hours", 8.0),
            "links": ", ".join([a for act in entry.get("activities", []) for a in act.get("artifacts", [])]),
            "learnings": entry.get("learnings", "Applied technical skills."),
            "blockers": entry.get("blockers", "None"),
            "skill_ids": "1"
        }
        
        submitter = None
        try:
            submitter = VTUSubmitter(headless=config.selenium_headless, wait_for_user=False)
            submitter.login_manually()
            status = submitter.fill_diary(data_to_fill, dry_run=False)
            
            append_audit({
                "event": "portal_submit",
                "status": status,
                "portal_response": "Selenium initiated"
            })
            return {"message": f"[OK] Status: {status}"}
            
        except SubmitError as e:
            if submitter: submitter.close()
            return JSONResponse({"error": f"Selenium error: {e}"}, status_code=500)
            
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/api/health")
async def health():
    return {"status": "healthy", "provider": config.llm_provider}
