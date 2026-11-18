from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import login_router, usuario_router, viaje_router, parcia_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.include_router(login_router.router)
app.include_router(usuario_router.router)
app.include_router(viaje_router.router)
app.include_router(parcia_router.router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request, "login.html")
