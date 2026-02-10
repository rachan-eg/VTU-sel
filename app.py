#!/usr/bin/env python3
"""Simple web UI for diary automation - FastAPI version"""
import os
import json
from pathlib import Path
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.llm_client import get_llm_client
from src.diary_formatter import validate_and_format
from src.selenium_submit import VTUSubmitter
from src.playwright.submitter import VTUSubmitterPlaywright
from src.utils.logger import get_logger
from main import transform_to_form_data

app = FastAPI(title="VTU Diary Automation")
templates = Jinja2Templates(directory="templates")
logger = get_logger(__name__)

# Store status for progress updates
status = {
    "running": False,
    "stage": "",
    "message": "",
    "success": False,
    "error": None
}

class DiarySubmission(BaseModel):
    content: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main UI"""
    return templates.TemplateResponse("simple.html", {"request": request})

@app.post("/submit")
async def submit(submission: DiarySubmission, background_tasks: BackgroundTasks):
    """Accept diary content and start processing"""
    global status

    if status["running"]:
        raise HTTPException(status_code=400, detail="Already running")

    if not submission.content.strip():
        raise HTTPException(status_code=400, detail="No content provided")

    # Start automation in background
    background_tasks.add_task(run_automation_task, submission.content.strip())

    return {"status": "started"}

@app.get("/status")
async def get_status():
    """Return current automation status"""
    return status

async def run_automation_task(raw_content: str):
    """Main automation task - runs in background"""
    global status

    status = {
        "running": True,
        "stage": "ai",
        "message": "Processing with AI...",
        "success": False,
        "error": None
    }

    try:
        # AI Processing
        logger.info("AI processing...")
        llm = get_llm_client()
        system_prompt = Path("system_prompts/diary_generator_system.txt").read_text()
        prompt = f"Transform this into a diary entry:\n\n{raw_content}"

        response = llm.generate(system=system_prompt, prompt=prompt)
        # response is already a dict (parsed by LLM client)
        diary_data = response if isinstance(response, dict) else json.loads(response)

        entry = validate_and_format(diary_data)
        form_data = transform_to_form_data(diary_data)

        status["message"] = f"AI done. Date: {entry.date}"

        # Browser Automation
        status["stage"] = "browser"
        status["message"] = "Opening browser and logging in..."
        logger.info("Starting browser automation...")

        # Choose browser engine: selenium or playwright
        browser_engine = os.getenv("BROWSER_ENGINE", "selenium").lower()
        headless = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"

        if browser_engine == "playwright":
            logger.info("Using Playwright engine")
            submitter = VTUSubmitterPlaywright(
                headless=headless,
                profile_name="default"
            )
        else:
            logger.info("Using Selenium engine")
            submitter = VTUSubmitter(
                headless=headless,
                wait_for_user=False
            )

        try:
            portal_url = os.getenv("PORTAL_LOGIN_URL")
            submitter.login_manually(portal_url)

            status["message"] = "Filling form..."
            result = submitter.fill_diary(form_data, dry_run=False)

            if result == "SUBMITTED" or (isinstance(result, dict) and result.get("success")):
                status["success"] = True
                status["stage"] = "done"
                status["message"] = f"Done! Diary submitted for {entry.date}"
            else:
                error_msg = result.get("error") if isinstance(result, dict) else str(result)
                raise Exception(f"Submission failed: {error_msg}")

        finally:
            submitter.close()

    except Exception as e:
        logger.error(f"Automation failed: {e}")
        status["error"] = str(e)
        status["stage"] = "error"
        status["message"] = f"Error: {e}"

    finally:
        status["running"] = False

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    uvicorn.run("app:app", host='0.0.0.0', port=port, reload=True)
