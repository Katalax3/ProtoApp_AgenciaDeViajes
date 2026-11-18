from pathlib import Path

from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from agencia_viajes_web.core.dependencies import NoAutenticadoVista
from .routers import login_router, usuario_router, viaje_router, empleado_router, dba_router
from .core.config import settings
from .core.templates import templates

app = FastAPI()

app.include_router(login_router.router)
app.include_router(usuario_router.router)
app.include_router(viaje_router.router)
app.include_router(empleado_router.router)
app.include_router(dba_router.router)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, max_age=settings.session_max_age)

@app.exception_handler(NoAutenticadoVista)
async def redirigir_a_login(request: Request, exc: NoAutenticadoVista):
  return RedirectResponse(
      url="/", status_code=302
  )

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request, "login.html")
