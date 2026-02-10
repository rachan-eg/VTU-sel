"""Enhanced FastAPI app with bulk submission and WebSocket support"""
import sys
import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Fix for Windows asyncio + Playwright subprocess issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from src.api import router, websocket_endpoint
from src.db import init_db
from config import API_HOST, API_PORT, DEBUG_MODE
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="VTU Diary Automation",
    description="Advanced bulk diary submission system with AI",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting VTU Diary Automation v2.0")
    init_db()
    logger.info("Database initialized")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve main UI"""
    return templates.TemplateResponse("index_bulk.html", {"request": request})


@app.get("/approval", response_class=HTMLResponse)
async def approval_page(request: Request):
    """Approval/preview page"""
    return templates.TemplateResponse("approval.html", {"request": request})


@app.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request):
    """Progress tracking page"""
    return templates.TemplateResponse("progress.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Submission history page"""
    return templates.TemplateResponse("history.html", {"request": request})


@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for progress updates"""
    await websocket_endpoint(websocket, session_id)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == '__main__':
    import uvicorn

    # Configure event loop for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    uvicorn.run(
        "app_new:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,  # Auto-reload on code changes
        reload_dirs=[".", "src", "templates"],  # Watch these directories
        log_level="info",
        loop="asyncio"  # Use asyncio event loop
    )
