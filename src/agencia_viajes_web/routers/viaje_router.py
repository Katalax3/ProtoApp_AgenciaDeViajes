from decimal import Decimal
from datetime import datetime
from agencia_viajes_web import Conexion
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from psycopg import Connection
from agencia_viajes_web.repositories.viaje_repo import ViajeRepo

class ViajeCreate(BaseModel):
    id_transporte: int
    id_ciudad_destino: int
    id_ciudad_origen: int
    fecha_salida: datetime
    fecha_llegada: datetime
    nombre: str
    costo: Decimal = Field(max_digits=8, decimal_places=2)

class ViajeRespose(BaseModel):
    id_viaje: int
    id_transporte: int
    id_ciudad_destino: int
    id_ciudad_origen: int
    fecha_salida: datetime
    fecha_llegada: datetime
    nombre: str
    costo: Decimal = Field(max_digits=8, decimal_places=2)


router = APIRouter(prefix="/viaje", tags=["Viaje"])

db_manager = Conexion()

@router.post("/", response_model=ViajeRespose)
def registrar_viaje(datos_registro: ViajeCreate, db: Connection = Depends(db_manager.get_db)):
    repo=ViajeRepo(conn=db)
    try:
        respuesta = repo.insertar_registro(datos_registro.model_dump())
        return respuesta
    except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))