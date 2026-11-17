from fastapi import FastAPI
from .routers import login_router, usuario_router, viaje_router, parcia_router

app = FastAPI()

app.include_router(login_router.router)
app.include_router(usuario_router.router)
app.include_router(viaje_router.router)
app.include_router(parcia_router.router)

@app.get("/")
def root():
    return {"Servidor": "Servidor funcionando correctamente"}
