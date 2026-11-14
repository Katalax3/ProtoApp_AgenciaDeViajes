from fastapi import FastAPI
from .routers import login_router

app = FastAPI()

app.include_router(login_router.router)

@app.get("/")
def root():
    return {"Servidor": "Servidor funcionando correctamente"}
