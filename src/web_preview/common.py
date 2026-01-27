from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

def timeformat(value):
    from datetime import datetime
    return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

templates.env.filters["timeformat"] = timeformat
