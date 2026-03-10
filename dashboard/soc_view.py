from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def soc_dashboard():
    html_file = Path(__file__).parent / "soc.html"

    if not html_file.exists():
        return HTMLResponse("<h1>soc.html not found</h1>", status_code=404)

    return HTMLResponse(html_file.read_text(encoding="utf-8"))
