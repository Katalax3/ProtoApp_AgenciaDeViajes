from fastapi.responses import RedirectResponse

from agencia_viajes_web import Conexion
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from psycopg import Connection
from agencia_viajes_web.repositories.login_repo import LoginRepo

class CredencialesCreate(BaseModel):
    correo: str
    contrasena: str

class CredencialesResponse(BaseModel):
    nombre: str
    paterno: str
    tipo_usuario: str

router = APIRouter(prefix="/login", tags=["Login"])

db_manager = Conexion()

@router.post("/", response_model=CredencialesResponse)
def login(request: Request, credenciales: CredencialesCreate, db: Connection = Depends(db_manager.get_db)):
    repo = LoginRepo(db)
    try:
        usuario = repo.validar_credenciales(credenciales.model_dump())

        request.session["usuario"] = {
            "nombre": usuario["nombre"],
            "paterno": usuario["paterno"],
            "tipo_usuario": usuario["tipo_usuario"],
        }

        return {
            "nombre": usuario["nombre"],
            "paterno": usuario["paterno"],
            "tipo_usuario": usuario["tipo_usuario"],
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/logout")
def logout(request: Request):
  request.session.clear()
  return RedirectResponse(url="/", status_code=302)