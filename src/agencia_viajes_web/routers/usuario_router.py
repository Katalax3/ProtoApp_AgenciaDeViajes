from typing import Optional, Literal
from agencia_viajes_web import Conexion
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg import Connection
from agencia_viajes_web.repositories.usuario_repo import UsuarioRepo

class UsuarioCreate(BaseModel):
    nombre: str
    paterno: str
    materno: Optional[str] = None
    telefono: Optional[str] = Field(default=None, max_length=13)
    correo: str
    contrasena: str
    tipo_usuario: Literal["Empleado", "Cliente", "DBA"]
    id_agencia: Optional[int] = None
    num_empleado: Optional[str] = Field(default=None, max_length=9)


class UsuarioRespose(BaseModel):
    id_usuario: int
    nombre: str
    paterno: str
    materno: Optional[str] = None
    telefono: Optional[str] = None
    correo: str
    tipo_usuario: Literal["Empleado", "Cliente", "DBA"]
    id_agencia: Optional[int] = None
    num_empleado: Optional[str] = None

router = APIRouter(prefix="/usuario", tags=["Usuario"])
db_manager = Conexion()

@router.post("/", response_model=UsuarioRespose)
def registrar_usuario(datos_registro: UsuarioCreate, db: Connection = Depends(db_manager.get_db)):
    repo=UsuarioRepo(conn=db)
    try:
        respuesta = repo.insertar_usuario(datos_registro.model_dump())
        return respuesta
    except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
