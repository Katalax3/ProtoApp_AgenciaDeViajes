from agencia_viajes_web import Conexion
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from psycopg import Connection
from agencia_viajes_web.repositories.usuario_repo import UsuarioRepo

class UsuarioCreate(BaseModel):
    nombre: str
    paterno: str
    materno: str
    telefono: str
    correo: str
    contrasena: str
    tipo_usuario: str
    id_agencia: int
    num_empleado: str


class UsuarioRespose(BaseModel):
    id_usuario: int
    nombre: str
    paterno: str
    materno: str
    telefono: str
    correo: str
    tipo_usuario: str
    id_agencia: int
    num_empleado: str

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
