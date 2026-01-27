import sys
import os
import json
from pathlib import Path
from datetime import datetime

from llm_client import LLMClient
from diary_formatter import validate_and_format, check_word_count
from audit import append_audit, read_audit, rotate_logs
from selenium_submit import VTUSubmitter
from config import Config, validate_config
from integrations.git_client import GitClient
from integrations.calendar_client import CalendarClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

def cmd_generate(args):
    """Generate diary entry from raw notes."""
    logger.info(f"Generating diary from: {args.input}")
    
    if args.input == "-":
        raw_text = sys.stdin.read()
    else:
        with open(args.input, "r") as f:
            raw_text = f.read()
    
    artifacts = {}
    if args.with_git:
        logger.info("Fetching git commits...")
        artifacts["commits"] = GitClient(args.git_repo or ".").get_today_commits()
    
    if args.with_calendar:
        logger.info("Fetching calendar events...")
        artifacts["events"] = CalendarClient().get_today_events()
    
    config = Config()
    client = LLMClient(provider=config.llm_provider)
    
    # Correct path to system prompts
    prompt_path = Path(__file__).parent.parent / "system_prompts" / "diary_generator_system.txt"
    if prompt_path.exists():
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    else:
        # Fallback/Debug
        logger.warning(f"System prompt not found at {prompt_path}, using default empty.")
        system_prompt = "You are a helpful assistant."

    if artifacts:
        raw_text += "\n\nADDITIONAL ARTIFACTS:\n" + json.dumps(artifacts, indent=2)
    
    try:
        result = client.generate_diary(raw_text, system_prompt)
        entry = validate_and_format(result)
        word_check = check_word_count(result["entry_text"])
        
        append_audit({
            "event": "cli_generate",
            "raw_text": raw_text,
            "llm_output": result,
            "word_count": word_check,
            "status": "generated"
        })
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            logger.info(f"Saved to: {args.output}")
        else:
            print(json.dumps(result, indent=2))
        
        logger.info("[OK] Complete")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)

def cmd_submit(args):
    """Submit diary entry to VTU portal."""
    logger.info("Starting submission flow...")
    
    if not args.entry:
        logger.error("No entry file provided.")
        sys.exit(1)

    with open(args.entry, "r") as f:
        entry = json.load(f)
    
    data = {
        "description": entry.get("entry_text", ""),
        "hours": args.hours or 8,
        "links": ", ".join([a for act in entry.get("activities", []) for a in act.get("artifacts", [])]),
        "learnings": args.learnings or "Applied technical problem-solving skills.",
        "blockers": args.blockers or "None",
        "skill_ids": args.skill_ids or ""
    }
    
    submitter = VTUSubmitter(headless=args.headless)
    try:
        if not args.skip_login:
            submitter.login_manually()
        status = submitter.fill_diary(data, dry_run=args.dry_run)
        
        append_audit({"event": "portal_submit", "status": status})
        logger.info(f"[OK] Submission status: {status}")
    except Exception as e:
        logger.error(f"Submission failed: {e}")
        sys.exit(1)
    finally:
        if not args.keep_browser:
            submitter.close()

def cmd_serve(args):
    """Start the web UI server."""
    logger.info(f"Starting web server on port {args.port}...")
    from web_preview.app import app
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

def cmd_audit(args):
    if args.action == "list":
        entries = read_audit()
        print(f"\nAudit Log ({len(entries)}):")
        for i, entry in enumerate(entries):
            ts = datetime.fromtimestamp(entry.get("timestamp", 0))
            print(f"{i+1}. [{ts}] {entry.get('event')} - {entry.get('status')}")
    elif args.action == "export":
        entries = read_audit()
        output = args.output or "audit_export.json"
        with open(output, "w") as f:
            json.dump(entries, f, indent=2)
    elif args.action == "rotate":
        rotate_logs()
    elif args.action == "clear":
        if input("Clear logs? [y/N] ").lower() == "y":
            if os.path.exists("audit_log.enc"): os.remove("audit_log.enc")

def cmd_validate(args):
    logger.info("Validating configuration...")
    errors = validate_config()
    if errors:
        for err in errors: logger.error(f"[FAIL] {err}")
        sys.exit(1)
    logger.info("[OK] Configuration valid")
