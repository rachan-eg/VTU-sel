import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from config import Config
from utils.logger import setup_logger
from .routes.pages import router as pages_router
from .routes.api import router as api_router

logger = setup_logger(__name__)
config = Config()

app = FastAPI(title="VTU Automation Web UI")
app.add_middleware(SessionMiddleware, secret_key=config.flask_secret_key)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

app.include_router(pages_router)
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    uvicorn.run(app, host=host, port=port)
