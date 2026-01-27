from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from ..common import templates
from audit import read_audit
from llm_client import LLMClient
from diary_formatter import check_word_count
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/generate_ui", response_class=HTMLResponse)
async def generate_ui(request: Request):
    return templates.TemplateResponse("generate.html", {"request": request})

@router.get("/preview", response_class=HTMLResponse)
async def preview(request: Request):
    entry = request.session.get('last_entry')
    word_check = request.session.get('word_check', {})
    usage_stats = request.session.get('usage_stats', {})
    
    if not entry:
        try:
            client = LLMClient(provider="mock")
            entry = client.generate_diary("", "")
            word_check = check_word_count(entry["entry_text"])
        except Exception as e:
            logger.error(f"Failed to load example: {e}")
            return RedirectResponse(url="/generate_ui")
    
    return templates.TemplateResponse("preview.html", {
        "request": request, 
        "entry": entry, 
        "word_check": word_check, 
        "usage_stats": usage_stats
    })

# Add missing submit_ui route that redirects to preview or shows a dedicated submit page
@router.get("/submit_ui", response_class=HTMLResponse)
async def submit_ui_page(request: Request):
    # For now, we can reuse preview or redirect to it
    return RedirectResponse(url="/preview")

@router.get("/audit", response_class=HTMLResponse)
async def audit(request: Request):
    try:
        entries = read_audit()
        return templates.TemplateResponse("audit.html", {"request": request, "entries": entries})
    except Exception as e:
        logger.error(f"Audit read error: {e}")
        return HTMLResponse(content=f"Error reading audit log: {e}", status_code=500)
