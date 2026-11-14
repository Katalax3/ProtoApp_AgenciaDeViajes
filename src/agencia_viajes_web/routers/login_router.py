from agencia_viajes_web import Conexion
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from psycopg import Connection
from agencia_viajes_web.repositories.login_repo import LoginRepo

class CredencialesCreate(BaseModel):
    correo: str
    contrasena: str

class CredencialesResponse(BaseModel):
    correo: str

router = APIRouter(prefix="/login", tags=["Login"])

db_manager = Conexion()

@router.post("/")
def login(credenciales: CredencialesCreate, db: Connection = Depends(db_manager.get_db)):
    repo = LoginRepo(db)
    try:
        tipo_usuario = repo.validar_credenciales(credenciales.model_dump())
        return {
            "mensaje": "Login exitoso",
            "tipo_usuario": tipo_usuario
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))